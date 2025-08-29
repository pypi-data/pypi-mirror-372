import pandas as pd
import numpy as np
import os
import ast
import time
import sys
from datetime import timedelta, datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import gc
from typing import Dict, List, Tuple, Optional, Union
from datupapi.utils.utils import Utils
from datupapi.inventory.src.SuggestedForecast.suggested_forecast import SuggestedForecast
from datupapi.inventory.src.FutureInventory.daily_usage_future import DailyUsageFuture


def _generate_item_dates_worker(key, df_lead_time, periods, period2, start_date, start_date_zero, default_coverage, location):
    """
    Generate dates for a single item in the worker process context.
    This function replicates the logic from future_date() but for a single item.
    
    Args:
        key: Item identifier (str) or (item, location) tuple
        df_lead_time: Lead time DataFrame (filtered for this item)
        periods: Number of periods to generate (for ReorderFreq > 20)
        period2: Number of periods to generate (for ReorderFreq <= 20)
        start_date: Start date for period 1 (can be None)
        start_date_zero: Custom start date for period 0 (can be None)
        default_coverage: Default coverage days
        location: Boolean indicating location-based processing
                 (Note: This parameter is kept for interface consistency but is not
                 directly used in date generation logic, as dates depend on ReorderFreq
                 which is already in the filtered df_lead_time)
        
    Returns:
        List[str]: List of dates in 'YYYYMMDD' format
    """
    try:
        # Determine the starting date for period 0
        if start_date_zero is not None:
            # Use custom start date for period 0
            actual_date = pd.to_datetime(start_date_zero, format='%Y-%m-%d')
        else:
            # Use current system date for period 0 (original behavior)
            DOCKER_CONFIG_PATH = os.path.join('/opt/ml/processing/input', 'config.yml')
            utils = Utils(config_file=DOCKER_CONFIG_PATH, logfile='data_io', log_path='output/logs')
            timestamp = utils.set_timestamp()
            actual_date = pd.to_datetime(str(int(float(timestamp[0:8]))), format='%Y%m%d')
        
        # Determine which period count to use based on ReorderFreq
        reorder_freq = df_lead_time['ReorderFreq'].iloc[0]
        if pd.isna(reorder_freq) or reorder_freq == 0:
            reorder_freq = default_coverage
        reorder_freq = int(reorder_freq)
        
        # Use period2 for ReorderFreq <= 20, otherwise use periods
        if reorder_freq <= 20:
            effective_periods = period2
        else:
            effective_periods = periods
        
        # Use effective_periods + 1 internally to calculate one extra period for transit calculations
        end_date = actual_date + pd.DateOffset(months=effective_periods + 1)
        
        # Handle start_date = None case
        if start_date is None:
            # If start_date is None, use actual_date as the base for period 1
            base_start_date = actual_date
        else:
            base_start_date = pd.to_datetime(start_date, format='%Y-%m-%d')
        
        # ReorderFreq was already calculated above, no need to recalculate
        
        # Generate date range for this item
        date_range = []
        
        # Always include actual date (period 0)
        date_range.append(actual_date)
        
        # Include base_start_date if after actual_date
        if base_start_date > actual_date:
            date_range.append(base_start_date)
        
        # Generate subsequent dates using a controlled loop instead of pd.date_range
        current_date = base_start_date + timedelta(days=reorder_freq)
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=reorder_freq)
        
        # Convert to string format
        date_strings = [d.strftime('%Y%m%d') for d in date_range]
        
        return date_strings
        
    except Exception as e:
        print(f"Error generating dates for item {key}: {str(e)}")
        # Return a minimal date list with just the current date
        try:
            if start_date_zero is not None:
                actual_date = pd.to_datetime(start_date_zero, format='%Y-%m-%d')
            else:
                DOCKER_CONFIG_PATH = os.path.join('/opt/ml/processing/input', 'config.yml')
                utils = Utils(config_file=DOCKER_CONFIG_PATH, logfile='data_io', log_path='output/logs')
                timestamp = utils.set_timestamp()
                actual_date = pd.to_datetime(str(int(float(timestamp[0:8]))), format='%Y%m%d')
            return [actual_date.strftime('%Y%m%d')]
        except:
            # Last resort: return today's date
            return [datetime.now().strftime('%Y%m%d')]


def process_item_batch_complete(batch_args):
    """
    Process a batch of items in parallel with complete functionality.
    
    This function executes in a separate process and handles batch processing
    of inventory items for reorder calculations. It provides optimized error
    handling and progress tracking for large-scale inventory processing.
    
    Args:
        batch_args (tuple): Contains all necessary data for batch processing:
            - batch_items: List of item data tuples (key, lead_time_df, inv_df)
            - df_fcst: Forecast data DataFrame
            - df_prep: Preparation data DataFrame
            - metadata: List of metadata columns
            - location: Boolean indicating if location processing is enabled
            - default_coverage: Default coverage days
            - complete_suggested: Boolean for complete suggested forecast mode
            - security_stock_ref: Boolean for reference-based security stock calculation
            - integer: Boolean for integer formatting of quantities
            - verbose: Boolean for detailed logging
            - df_transit: Transit schedule DataFrame (optional)
            - periods: Number of periods to generate
            - start_date: Start date for period 1 (can be None)
            - start_date_zero: Custom start date for period 0 (can be None)
    
    Returns:
        pd.DataFrame: Combined results for all items in the batch, or empty DataFrame if errors
    """
    try:
        (batch_items, df_fcst, df_prep, metadata, location, default_coverage,
         complete_suggested, security_stock_ref, integer, verbose, df_transit,
         periods, period2, start_date, start_date_zero) = batch_args
        
        results = []
        processed_count = 0
        error_count = 0
        
        for item_data in batch_items:
            key, current_df_lead_time, current_df_inv = item_data
            
            try:
                # Generate dates for this item locally in the worker process
                dates = _generate_item_dates_worker(
                    key, current_df_lead_time, periods, period2, start_date,
                    start_date_zero, default_coverage, location
                )
                
                # Procesar este ítem usando la lógica completa con timeout implícito
                item_result = _process_item_complete(
                    key, dates, current_df_lead_time, current_df_inv,
                    df_fcst, df_prep, metadata, location, default_coverage,
                    complete_suggested, security_stock_ref, integer,
                    df_transit
                )
                
                if item_result is not None and not item_result.empty:
                    results.append(item_result)
                    processed_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                if verbose and error_count <= 3:  # Limit error messages to avoid spam
                    print(f"⚠️  Error procesando {key}: {str(e)[:100]}...")
                continue
        
        # Log batch summary if there were errors
        if verbose and error_count > 0:
            print(f"📊 Batch summary: {processed_count} processed, {error_count} errors")
        
        # Combine all items in this batch
        if results:
            return pd.concat(results, ignore_index=True)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Error crítico en batch: {str(e)}")
        return pd.DataFrame()


def _process_item_complete(key, dates, current_df_lead_time, current_df_inv,
                           df_fcst, df_prep, metadata, location, default_coverage,
                           complete_suggested, security_stock_ref, integer, df_transit=None):
    """
    Process a single item through all periods with complete functionality.
    
    This function handles the complete inventory reorder calculation for a single item
    across all time periods. It optimizes performance by pre-allocating data structures
    and reducing repetitive calls to forecast and daily usage calculations.
    
    The process includes:
    1. Calculating suggested forecasts for each period
    2. Computing daily usage rates (average and maximum)
    3. Determining security stock requirements
    4. Processing current period inventory
    5. Calculating future period reorder needs
    6. Managing transit order schedules
    7. Computing final inventory metrics
    
    Args:
        key: Item identifier (str) or (item, location) tuple
        dates: List of calculation dates in 'YYYYMMDD' format
        current_df_lead_time: Lead time data for this item
        current_df_inv: Current inventory data for this item
        df_fcst: Forecast data DataFrame
        df_prep: Preparation data DataFrame
        metadata: List of metadata columns
        location: Boolean indicating location-based processing
        default_coverage: Default coverage days
        complete_suggested: Boolean for complete suggested forecast mode
        security_stock_ref: Boolean for reference-based security stock
        integer: Boolean for integer formatting
        df_transit: Transit schedule DataFrame (optional)
    
    Returns:
        pd.DataFrame: Complete reorder calculations for all periods of this item
    """
    try:
        # Pre-allocate dictionaries for intermediate results
        suggested_forecasts = {}
        df_avgs = {}
        df_maxs = {}
        df_sstocks = {}
        period_results = {}
        
        # Initialize transit orders for this item
        transit_orders = {key: []}
        
        # Track last suggested forecast value for complete_suggested feature
        last_suggested_value = None
        
        # Pre-calculate common values to avoid repeated calculations
        coverage = current_df_lead_time['Coverage'].iloc[0] if 'Coverage' in current_df_lead_time.columns else default_coverage
        if pd.isna(coverage):
            coverage = default_coverage
        
        reorder_freq = current_df_lead_time['ReorderFreq'].iloc[0]
        if pd.isna(reorder_freq) or reorder_freq == 0:
            reorder_freq = default_coverage
        
        # Process each period with optimized error handling
        for i, date in enumerate(dates):
            try:
                # Calculate suggested forecast with better error handling
                suggested_forecasts[i] = _calculate_suggested_forecast_complete(
                    current_df_lead_time, current_df_inv, date, last_suggested_value,
                    df_fcst, df_prep, metadata, location, default_coverage, complete_suggested
                )
                
                # Update last_suggested_value for next iteration
                if 'SuggestedForecast' in suggested_forecasts[i].columns:
                    new_suggested_value = suggested_forecasts[i]['SuggestedForecast'].iloc[0]
                    
                    # Only update if the new value is not NaN
                    if not pd.isna(new_suggested_value):
                        last_suggested_value = new_suggested_value
                
                # Calculate daily usage with optimized calls
                df_avgs[i], df_maxs[i] = _calculate_daily_usage_complete(
                    suggested_forecasts[i], date, df_fcst, location
                )
                
                # Calculate security stock data with pre-calculated values
                df_sstocks[i] = _calculate_security_stock_data_complete(
                    df_maxs[i], current_df_lead_time, default_coverage, i, dates
                )
                
                # Process period based on whether it's current or future
                if i == 0:
                    period_results[i] = _process_current_period_complete(
                        current_df_inv, df_sstocks[i], key, date, transit_orders, dates,
                        metadata, integer, security_stock_ref, df_transit
                    )
                else:
                    period_results[i] = _process_future_period_complete(
                        current_df_inv, df_sstocks[i], period_results[i-1],
                        key, date, dates, i, transit_orders, metadata, integer, security_stock_ref
                    )
                
                # Add metadata columns efficiently
                period_results[i]['Date'] = date
                if location:
                    item, loc = key
                    period_results[i]['Item'] = item
                    period_results[i]['Location'] = loc
                else:
                    period_results[i]['Item'] = key
                    
            except Exception as e:
                # Log error but continue with next period
                import traceback
                tb = traceback.extract_tb(e.__traceback__)
                function_name = tb[-1].name if tb else 'unknown'
                line_number = tb[-1].lineno if tb else 'unknown'
                
                print(f"Warning: Error processing period {i} for item {key}:")
                print(f"   Function: {function_name} (line {line_number})")
                print(f"   Error: {str(e)}")
                print(f"   Error type: {type(e).__name__}")
                print(f"   Date value: {repr(date)} (type: {type(date)})")
                print(f"   Period index: {i}")
                print(f"   Total dates available: {len(dates)}")
                
                # Print more context for debugging
                if hasattr(e, '__cause__') and e.__cause__:
                    print(f"   Caused by: {str(e.__cause__)}")
                
                # Print the full traceback for error analysis
                print(f"   Full traceback:")
                traceback.print_exc()
                
                continue
    
        # After processing all periods, update FutureInventoryTransitArrival
        for i in range(len(dates)):
            if i < len(dates) - 1:  # If there's a next period
                # Get next period's TransitArrival
                next_transit_arrival = period_results[i + 1]['TransitArrival'].iloc[0]
                transit_arrival_sum = _sum_transit_arrivals(next_transit_arrival)
            else:  # Last period - no next period
                transit_arrival_sum = 0
            
            # Update FutureInventoryTransitArrival
            period_results[i]['FutureInventoryTransitArrival'] = _format_value_complete(
                period_results[i]['FutureInventory'].iloc[0] + transit_arrival_sum,
                'FutureInventoryTransitArrival', integer
            )
            
            # Recalculate FutureStockoutDays with the updated FutureInventoryTransitArrival
            period_results[i]['FutureStockoutDays'] = _calculate_inventory_days_complete(
                period_results[i], integer
            )
        
        # Combine all periods for this item
        if period_results:
            # Stack all period results at once
            item_df = pd.concat(period_results.values(), ignore_index=True)
            
            # Reorder columns for consistency
            cols = ['Date', 'Item']
            if location:
                cols.append('Location')
            other_cols = [col for col in item_df.columns if col not in cols]
            item_df = item_df[cols + other_cols]
            
            return item_df
        
        return None
        
    except Exception as e:
        # Handle any unexpected errors at the item level
        import traceback
        tb = traceback.extract_tb(e.__traceback__)
        function_name = tb[-1].name if tb else 'unknown'
        line_number = tb[-1].lineno if tb else 'unknown'
        
        print(f"Error processing item {key}:")
        print(f"   Function: {function_name} (line {line_number})")
        print(f"   Error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Item dates: {dates[:5] if dates else 'None'}... (showing first 5)")
        print(f"   Total dates: {len(dates) if dates else 0}")
        
        # Print more context for debugging
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"   Caused by: {str(e.__cause__)}")
        
        # Print the full traceback for error analysis
        print(f"   Full traceback:")
        traceback.print_exc()
        
        return None


def _format_value_complete(value, field_name, integer):
    """Apply appropriate formatting based on field type and integer setting."""
    # Handle pandas Series - extract scalar value
    if isinstance(value, pd.Series):
        if len(value) == 1:
            value = value.iloc[0]
        else:
            raise ValueError(f"Expected scalar value for {field_name}, got Series with {len(value)} elements")
    
    # Handle NaN, None, and infinite values
    if pd.isna(value) or value is None:
        return 0
    if np.isinf(value):
        return 0
        
    # Fields that are ALWAYS integers
    always_integer_fields = [
        'PurchaseFactor', 'AvgLeadTime', 'MaxLeadTime',
        'ReorderQtyDays', 'ReorderFreq', 'Coverage', 'FutureStockoutDays'
    ]
    
    # Fields that are ALWAYS decimals (2 decimal places)
    always_decimal_fields = ['AvgDailyUsage', 'MaxDailyUsage']
    
    # Fields that change based on integer setting
    quantity_fields = [
        'FutureInventoryTransit', 'FutureInventory', 'FutureTransit',
        'FutureInventoryTransitArrival', 'SuggestedForecast', 'SuggestedForecastPeriod',
        'ReorderPoint', 'ReorderQtyBase', 'ReorderQty', 'SecurityStock', 'Inventory', 'Transit'
    ]
    
    if field_name in always_integer_fields:
        return int(round(value))
    elif field_name in always_decimal_fields:
        return round(value, 2)
    elif field_name in quantity_fields:
        if integer:
            return int(round(value))
        else:
            return round(value, 2)
    else:
        # Default: return as is
        return value


def _suggested_forecast_fallback(current_df_lead_time, current_df_inv, date, df_fcst, metadata, location, default_coverage):
    """
    Simplified SuggestedForecast fallback function for multiprocessing compatibility.
    
    This function provides a basic forecast calculation when the main SuggestedForecast class fails
    due to multiprocessing issues. It calculates the forecast using an average-based approach:
    
    1. Sum all forecasts in the coverage period
    2. Calculate daily average (sum / total_days_in_period)
    3. Multiply by coverage days
    4. Round up to nearest integer
    
    Args:
        current_df_lead_time: Lead time DataFrame for this item
        current_df_inv: Inventory DataFrame for this item
        date: Date string in 'YYYYMMDD' format
        df_fcst: Forecast DataFrame
        metadata: List of metadata columns
        location: Boolean indicating location-based processing
        default_coverage: Default coverage days
        
    Returns:
        pd.DataFrame: DataFrame with SuggestedForecast column
    """
    try:
        # Parse the date
        current_date = pd.to_datetime(date, format='%Y%m%d')
        
        # Get coverage for this item
        coverage = current_df_lead_time['Coverage'].iloc[0] if 'Coverage' in current_df_lead_time.columns else default_coverage
        if pd.isna(coverage):
            coverage = default_coverage
        coverage = int(coverage)
        
        # Calculate forecast end date
        forecast_end_date = current_date + timedelta(days=coverage)
        
        # Filter forecast data for this item and date range
        if location:
            item = current_df_inv['Item'].iloc[0]
            loc = current_df_inv['Location'].iloc[0]
            forecast_mask = (df_fcst['Item'] == item) & (df_fcst['Location'] == loc)
        else:
            item = current_df_inv['Item'].iloc[0]
            forecast_mask = df_fcst['Item'] == item
        
        # Add date range filter - get all forecast data for this item
        forecast_mask &= (df_fcst['Date'] >= current_date) & (df_fcst['Date'] <= forecast_end_date)
        
        item_forecast = df_fcst[forecast_mask]
        
        # Calculate suggested forecast using average-based approach
        if not item_forecast.empty and 'Forecast' in item_forecast.columns:
            # Step 1: Sum all forecasts in the period
            total_forecast = item_forecast['Forecast'].sum()
            
            # Step 2: Calculate total days in the forecast period
            # Simplification: assume 30 days per month for calculation
            total_days_in_period = len(item_forecast)  # Number of forecast records
            if total_days_in_period == 0:
                suggested_forecast = 0.0
            else:
                # Step 3: Calculate daily average
                daily_average = total_forecast / total_days_in_period
                
                # Step 4: Multiply by coverage days
                suggested_forecast = daily_average * coverage
                
                # Step 5: Round up to nearest integer
                suggested_forecast = np.ceil(suggested_forecast)
            
            
        else:
            # Fallback: use 0 if no forecast data available
            suggested_forecast = 0.0
            item = current_df_inv['Item'].iloc[0]
            location_msg = ""
            if location and 'Location' in current_df_inv.columns:
                loc = current_df_inv['Location'].iloc[0]
                location_msg = f" at location {loc}"
            print(f"   ⚠️ No forecast data found for item {item}{location_msg}, using 0")
        
        # Create result DataFrame
        result_df = current_df_inv[metadata].copy()
        result_df['SuggestedForecast'] = suggested_forecast
        
        # Add required columns
        result_df['PurchaseFactor'] = current_df_inv.get('PurchaseFactor', pd.Series([1])).iloc[0]
        result_df['ItemDescription'] = current_df_inv.get('ItemDescription', pd.Series([''])).iloc[0]
        
        return result_df
        
    except Exception as e:
        print(f"   ❌ Fallback SuggestedForecast also failed: {str(e)}")
        # Last resort: return basic structure with 0 forecast
        result_df = current_df_inv[metadata].copy()
        result_df['SuggestedForecast'] = 0.0
        result_df['PurchaseFactor'] = current_df_inv.get('PurchaseFactor', pd.Series([1])).iloc[0]
        result_df['ItemDescription'] = current_df_inv.get('ItemDescription', pd.Series([''])).iloc[0]
        return result_df


def _calculate_suggested_forecast_complete(current_df_lead_time, current_df_inv, date, last_suggested_value,
                                          df_fcst, df_prep, metadata, location, default_coverage, complete_suggested):
    """Calculate suggested forecast for the given date using the SuggestedForecast class."""
    # Convert current date to datetime
    try:
        current_date = pd.to_datetime(date, format='%Y%m%d')
    except Exception as e:
        raise ValueError(f"_calculate_suggested_forecast_complete: Invalid date '{date}' - {str(e)}")
    
    # Get the maximum forecast date available
    max_forecast_date = df_fcst['Date'].max()
    
    # Get coverage value for this item
    coverage = current_df_lead_time['Coverage'].iloc[0] if 'Coverage' in current_df_lead_time.columns else default_coverage
    if pd.isna(coverage):
        coverage = default_coverage
    
    # Calculate the required forecast end date
    required_forecast_end_date = current_date + timedelta(days=int(coverage))
    
    # Check if we have sufficient forecast data
    if max_forecast_date < required_forecast_end_date:
        if complete_suggested:
            if last_suggested_value is not None:
                # Use the last calculated SuggestedForecast value
                result_df = current_df_inv[metadata].copy()
                result_df['SuggestedForecast'] = last_suggested_value
                
                # Add PurchaseFactor and ItemDescription from inventory data using safe access
                result_df['PurchaseFactor'] = current_df_inv.get('PurchaseFactor', pd.Series([1])).iloc[0]
                result_df['ItemDescription'] = current_df_inv.get('ItemDescription', pd.Series([''])).iloc[0]

                return result_df
            else:
                # For the first period when complete_suggested=True but no previous value exists
                try:
                    return SuggestedForecast(
                        df_LeadTimes=current_df_lead_time,
                        df_Forecast=df_fcst,
                        df_Prep=df_prep,
                        df_inv=current_df_inv,
                        column_forecast='SuggestedForecast',
                        columns_metadata=metadata,
                        frequency_='M',
                        location=location,
                        actualdate=date,
                        default_coverage_=default_coverage,
                        join_='left'
                    ).suggested_forecast()
                except Exception as e:
                    print(f"   ❌ Initial calculation failed: {str(e)}")
                    print(f"   🔄 Attempting fallback SuggestedForecast calculation...")
                    
                    try:
                        # Use simplified fallback function
                        fallback_result = _suggested_forecast_fallback(
                            current_df_lead_time, current_df_inv, date, df_fcst,
                            metadata, location, default_coverage
                        )
                        
                        return fallback_result
                        
                    except Exception as fallback_error:
                        print(f"   ❌ Fallback initial calculation also failed: {str(fallback_error)}")
                        
                        # Get item identifier for error message
                        item = current_df_inv['Item'].iloc[0]
                        location_msg = ""
                        if location and 'Location' in current_df_inv.columns:
                            loc = current_df_inv['Location'].iloc[0]
                            location_msg = f" at location {loc}"
                        
                        error_msg = (
                            f"Cannot calculate initial forecast for item {item}{location_msg}. "
                            f"Forecast data extends only to {max_forecast_date.strftime('%Y-%m-%d')}, "
                            f"but coverage of {int(coverage)} days from {current_date.strftime('%Y-%m-%d')} "
                            f"requires forecast data until {required_forecast_end_date.strftime('%Y-%m-%d')}. "
                            f"Original error: {str(e)}"
                        )
                        raise ValueError(error_msg)
        else:
            # Get item identifier for error message
            item = current_df_inv['Item'].iloc[0]
            location_msg = ""
            if location and 'Location' in current_df_inv.columns:
                loc = current_df_inv['Location'].iloc[0]
                location_msg = f" at location {loc}"
            
            error_msg = (
                f"Insufficient forecast data for item {item}{location_msg}. "
                f"Forecast data extends only to {max_forecast_date.strftime('%Y-%m-%d')}, "
                f"but coverage of {int(coverage)} days from {current_date.strftime('%Y-%m-%d')} "
                f"requires forecast data until {required_forecast_end_date.strftime('%Y-%m-%d')}."
            )
            raise ValueError(error_msg)
    
    # If validation passes, proceed with the original calculation
    try:
        result = SuggestedForecast(
            df_LeadTimes=current_df_lead_time,
            df_Forecast=df_fcst,
            df_Prep=df_prep,
            df_inv=current_df_inv,
            column_forecast='SuggestedForecast',
            columns_metadata=metadata,
            frequency_='M',
            location=location,
            actualdate=date,
            default_coverage_=default_coverage,
            join_='left'
        ).suggested_forecast()
        
            
        return result
        
    except Exception as e:
        print(f"   ❌ Normal calculation failed: {str(e)}")
        print(f"   🔄 Attempting fallback SuggestedForecast calculation...")
        
        try:
            # Use simplified fallback function
            fallback_result = _suggested_forecast_fallback(
                current_df_lead_time, current_df_inv, date, df_fcst,
                metadata, location, default_coverage
            )
            
            
            return fallback_result
            
        except Exception as fallback_error:
            print(f"   ❌ Fallback calculation also failed: {str(fallback_error)}")
            # Re-raise the original error
            raise e


def _calculate_daily_usage_complete(suggested_forecast_df, date, df_fcst, location):
    """Calculate average and maximum daily usage rates."""
    
    try:
        df_avg = DailyUsageFuture(
            location=location,
            column_forecast='SuggestedForecast',
            date=date,
            df_fcst=df_fcst
        ).daily_usage(suggested_forecast_df, 'AvgDailyUsage').fillna(0)
        
        df_max = DailyUsageFuture(
            location=location,
            column_forecast='SuggestedForecast',
            date=date,
            df_fcst=df_fcst
        ).daily_usage(df_avg, 'MaxDailyUsage').fillna(0)
        
    except Exception as e:
        print(f"   ❌ DailyUsageFuture error: {str(e)}")
        print(f"   ❌ Error type: {type(e).__name__}")
        
        # Print more detailed error info
        import traceback
        print(f"   ❌ Full traceback:")
        traceback.print_exc()
        
        # Re-raise the original error to maintain the error flow
        raise e
    
    return df_avg, df_max


def _calculate_security_stock_data_complete(df_max, current_df_lead_time, default_coverage, period_index, dates):
    """
    Calculate security stock related data and prepare for reorder calculations.
    
    This function merges daily usage data with lead time information and calculates
    the suggested forecast period based on coverage ratios. For period 0, it uses
    days to the next period instead of reorder frequency for more accurate consumption.
    
    The process includes:
    1. Merging daily usage with lead time data
    2. Determining effective reorder frequency and coverage
    3. Calculating SuggestedForecastPeriod based on coverage ratio
    4. Special handling for period 0 using actual days to next period
    
    Args:
        df_max: DataFrame with maximum daily usage
        current_df_lead_time: Lead time data for current item
        default_coverage: Default coverage days
        period_index: Current period index (0, 1, 2, ...)
        dates: List of dates for this item
        
    Returns:
        pd.DataFrame: DataFrame with merged data and calculated fields including
                     SuggestedForecastPeriod adjusted for the specific period
    """
    metadata = ['Item', 'Location'] if 'Location' in df_max.columns else ['Item']
    merge_columns = ['Item', 'Location', 'AvgLeadTime', 'MaxLeadTime'] if 'Location' in df_max.columns else ['Item', 'AvgLeadTime', 'MaxLeadTime']
    df_sstock = pd.merge(df_max, current_df_lead_time[merge_columns], on=metadata, how='inner').drop_duplicates()
    
    # Get ReorderFreq and Coverage
    reorder_freq = current_df_lead_time['ReorderFreq'].values[0]
    if pd.isnull(reorder_freq) or reorder_freq == 0:
        reorder_freq = default_coverage
        
    coverage = default_coverage
    if 'Coverage' in current_df_lead_time.columns:
        coverage_val = current_df_lead_time['Coverage'].values[0]
        if not pd.isnull(coverage_val):
            coverage = coverage_val
        else:
            coverage = reorder_freq + df_sstock['AvgLeadTime'].values[0]
    else:
        coverage = reorder_freq + df_sstock['AvgLeadTime'].values[0]
    
    # Calculate SuggestedForecastPeriod
    if period_index == 0 and dates is not None and len(dates) > 1:
        # For period 0, use days to next period instead of reorder frequency
        try:
            # Validate dates array and indices
            if len(dates) < 2:
                raise ValueError(f"Insufficient dates for period 0 calculation: need at least 2 dates, got {len(dates)}")
            
            # Validate date formats before conversion
            if not isinstance(dates[0], str) or len(dates[0]) != 8:
                raise ValueError(f"Invalid dates[0] format: {repr(dates[0])} (expected 8-character string)")
            if not isinstance(dates[1], str) or len(dates[1]) != 8:
                raise ValueError(f"Invalid dates[1] format: {repr(dates[1])} (expected 8-character string)")
            
            current_date = pd.to_datetime(dates[0], format='%Y%m%d')
            next_date = pd.to_datetime(dates[1], format='%Y%m%d')
            
        except Exception as e:
            error_msg = f"_calculate_security_stock_data_complete: Date processing error - "
            error_msg += f"dates[0]='{dates[0] if len(dates) > 0 else 'MISSING'}' "
            error_msg += f"(type: {type(dates[0]) if len(dates) > 0 else 'N/A'}), "
            error_msg += f"dates[1]='{dates[1] if len(dates) > 1 else 'MISSING'}' "
            error_msg += f"(type: {type(dates[1]) if len(dates) > 1 else 'N/A'}), "
            error_msg += f"period_index={period_index}, dates_length={len(dates)}, "
            error_msg += f"original_error: {str(e)}"
            raise ValueError(error_msg)
        days_to_next_period = (next_date - current_date).days
        
        # Formula: SuggestedForecast × (days_to_next_period / coverage)
        suggested_forecast_period = np.ceil(df_sstock['SuggestedForecast'] * (days_to_next_period / coverage))
    else:
        # For other periods, use the original calculation with reorder frequency
        suggested_forecast_period = np.ceil(df_sstock['SuggestedForecast'] * (reorder_freq / coverage))
    
    df_sstock['SuggestedForecastPeriod'] = suggested_forecast_period.apply(
        lambda x: int(round(x))  # SuggestedForecastPeriod is always integer
    )
    
    return df_sstock


def _calculate_security_stock_complete(df, security_stock_ref, integer):
    """Calculate security stock using configured method. Replicates exactly the logic from future_reorder_optimized."""
    # EXACTLY like future_reorder_optimized line 528-536
    if security_stock_ref:
        if 'SecurityStockDaysRef' in df.columns:
            security_stock_value = df['SecurityStockDaysRef'].iloc[0] * df['AvgDailyUsage'].iloc[0]
        else:
            security_stock_value = 0
    else:
        security_stock_value = (df['MaxDailyUsage'].iloc[0] * df['MaxLeadTime'].iloc[0]) - (df['AvgDailyUsage'].iloc[0] * df['AvgLeadTime'].iloc[0])
    
    # Apply formatting and return as scalar
    return _format_value_complete(security_stock_value, 'SecurityStock', integer)


def _calculate_inventory_days_complete(df, integer):
    """Calculate inventory days using configured method."""
    # Calculate future stockout days with safe division
    future_stockout_days = np.where(
        df['AvgDailyUsage'] > 0,
        (df['FutureInventoryTransitArrival'] - df['SecurityStock']) / df['AvgDailyUsage'],
        0  # If no daily usage, return 0 days
    )

    # Apply formatting
    return pd.Series(future_stockout_days).apply(lambda x: _format_value_complete(x, 'FutureStockoutDays', integer))


def _sum_transit_arrivals(transit_arrivals_str):
    """Calculate the total quantity from TransitArrival string."""
    if transit_arrivals_str == '[]' or not transit_arrivals_str:
        return 0.0
        
    try:
        arrivals = ast.literal_eval(transit_arrivals_str)
        return sum(arrival.get('quantity', 0) for arrival in arrivals)
    except:
        return 0.0


def _prepare_transit_schedule_complete(key, transit_amount, dates, df_transit, location):
    """Prepare transit schedule based on df_transit or default logic."""
    if transit_amount <= 0:
        return []
        
    transit_schedule = []
    
    if df_transit is None:
        # Default logic: complete transit arrives in period 1
        if len(dates) > 1:
            try:
                arrival_date = pd.to_datetime(dates[1], format='%Y%m%d')
            except Exception as e:
                raise ValueError(f"_prepare_transit_schedule_complete: Invalid date dates[1]='{dates[1]}' - {str(e)}")
            transit_schedule.append({
                'quantity': transit_amount,
                'arrival_date': arrival_date
            })
    else:
        # Use provided transit schedule
        if location:
            item, loc = key
            mask = (df_transit['Item'] == item) & (df_transit['Location'] == loc)
        else:
            mask = df_transit['Item'] == key
            
        transit_data = df_transit[mask].copy()
        
        if not transit_data.empty:
            # Validate total matches
            total_scheduled = transit_data['Transit'].sum()
            if abs(total_scheduled - transit_amount) > 0.01:  # Allow small floating point differences
                raise ValueError(f"Transit schedule total ({total_scheduled}) does not match inventory transit ({transit_amount}) for {key}")
            
            # Create transit orders
            for _, row in transit_data.iterrows():
                arrival_date = pd.to_datetime(row['ArrivalDate'], format='%Y-%m-%d')
                transit_schedule.append({
                    'quantity': float(row['Transit']),
                    'arrival_date': arrival_date
                })
        else:
            # If no transit data provided for this item, use default logic
            if len(dates) > 1:
                try:
                    arrival_date = pd.to_datetime(dates[1], format='%Y%m%d')
                except Exception as e:
                    raise ValueError(f"_prepare_transit_schedule_complete: Invalid fallback date dates[1]='{dates[1]}' - {str(e)}")
                transit_schedule.append({
                    'quantity': transit_amount,
                    'arrival_date': arrival_date
                })
                
    return transit_schedule


def _process_current_period_complete(current_df_inv, df_sstock, key, date, transit_orders, dates, metadata, integer, security_stock_ref=False, df_transit=None):
    """Process inventory for the current period (i=0). Replicates exactly the logic from future_reorder_optimized."""
    
    # Get inventory data efficiently - EXACTLY like future_reorder_optimized line 410-414
    try:
        inventory_data = {
            'FutureInventory': current_df_inv['Inventory'].iloc[0],
            'FutureTransit': current_df_inv['Transit'].iloc[0],
            'PurchaseFactor': current_df_inv['PurchaseFactor'].iloc[0] if 'PurchaseFactor' in current_df_inv.columns else 1
        }
    except KeyError as e:
        # Handle missing columns gracefully
        inventory_data = {
            'FutureInventory': current_df_inv.get('Inventory', pd.Series([0])).iloc[0],
            'FutureTransit': current_df_inv.get('Transit', pd.Series([0])).iloc[0],
            'PurchaseFactor': current_df_inv.get('PurchaseFactor', pd.Series([1])).iloc[0]
        }
    
    # Vectorized calculations - EXACTLY like future_reorder_optimized line 417-428
    df = df_sstock.copy()
    df['FutureInventory'] = _format_value_complete(inventory_data['FutureInventory'], 'FutureInventory', integer)
    df['FutureTransit'] = _format_value_complete(inventory_data['FutureTransit'], 'FutureTransit', integer)
    df['FutureInventoryTransit'] = _format_value_complete(
        inventory_data['FutureInventory'] + inventory_data['FutureTransit'],
        'FutureInventoryTransit', integer
    )
    df['PurchaseFactor'] = inventory_data['PurchaseFactor']
    
    # Initialize transit orders - EXACTLY like future_reorder_optimized line 430-438
    if key not in transit_orders:
        transit_orders[key] = []
    
    # Handle transit schedule
    transit_qty = float(inventory_data['FutureTransit'])
    if transit_qty > 0:
        transit_schedule = _prepare_transit_schedule_complete(key, transit_qty, dates, df_transit, 'Location' in metadata)
        transit_orders[key].extend(transit_schedule)
    
    # Set initial values - EXACTLY like future_reorder_optimized line 440-452
    df['TransitArrival'] = '[]'
    df['SecurityStock'] = _calculate_security_stock_complete(df, security_stock_ref, integer)
    df['SuggestedForecast'] = _format_value_complete(df['SuggestedForecast'].iloc[0], 'SuggestedForecast', integer)
    df['ReorderPoint'] = _format_value_complete(
        max(0, df['SuggestedForecast'].iloc[0] + df['SecurityStock'].iloc[0]), 'ReorderPoint', integer
    )
    df['ReorderQtyBase'] = _format_value_complete(
        max(0, df['ReorderPoint'].iloc[0] - df['FutureInventoryTransit'].iloc[0]), 'ReorderQtyBase', integer
    )
    df['ReorderQty'] = 0
    df['ReorderQtyDays'] = 0
    df['ArrivalDate'] = ''
    
    return df


def _process_transit_orders_complete(transit_orders, key, current_date, previous_date):
    """Process transit orders and calculate arrivals for the current period."""
    # Get orders for this key, return early if none
    orders = transit_orders.get(key, [])
    if not orders:
        return 0, 0, []
    
    new_transit = 0
    remaining_orders = []
    transit_arrivals = []
    stock_from_arrivals = 0
    
    for order in orders:
        if order['arrival_date'] > previous_date and order['arrival_date'] <= current_date:
            # Order arrives in this period
            stock_from_arrivals += order['quantity']
            transit_arrivals.append({
                'quantity': float(order['quantity']),
                'arrival_date': order['arrival_date'].strftime('%Y-%m-%d')
            })
        else:
            # Order still in transit
            new_transit += order['quantity']
            remaining_orders.append(order)
    
    transit_orders[key] = remaining_orders
    return stock_from_arrivals, new_transit, transit_arrivals


def _process_future_period_complete(current_df_inv, df_sstock, df_previous, key, date, dates, i, transit_orders, metadata, integer, security_stock_ref=False):
    """Process inventory for future periods (i>0). Replicates exactly the logic from future_reorder_optimized."""
    
    # EXACTLY like future_reorder_optimized line 460-461
    df = df_sstock.copy()
    try:
        df['PurchaseFactor'] = current_df_inv['PurchaseFactor'].iloc[0] if 'PurchaseFactor' in current_df_inv.columns else 1
    except (KeyError, IndexError):
        df['PurchaseFactor'] = 1
    
    # Calculate consumption - EXACTLY like future_reorder_optimized line 463-465
    consumption = df_previous['SuggestedForecastPeriod'].iloc[0]
    previous_stock = df_previous['FutureInventory'].iloc[0] - consumption
    
    # Process transit orders - EXACTLY like future_reorder_optimized line 467-473
    try:
        # Validate indices before accessing dates array
        if i <= 0:
            raise ValueError(f"Invalid period index {i} for future period processing (must be > 0)")
        if i-1 >= len(dates):
            raise ValueError(f"Previous period index {i-1} is out of bounds for dates array of length {len(dates)}")
        
        # Validate date values before conversion
        if not isinstance(date, str) or len(date) != 8:
            raise ValueError(f"Invalid current date format: {repr(date)} (expected 8-character string)")
        if not isinstance(dates[i-1], str) or len(dates[i-1]) != 8:
            raise ValueError(f"Invalid previous date format: {repr(dates[i-1])} (expected 8-character string)")
        
        current_date = pd.to_datetime(date, format='%Y%m%d')
        previous_date = pd.to_datetime(dates[i-1], format='%Y%m%d')
        
    except Exception as e:
        error_msg = f"_process_future_period_complete: Date processing error - "
        error_msg += f"current='{date}' (type: {type(date)}), "
        error_msg += f"previous='{dates[i-1] if i-1 < len(dates) else 'INDEX_OUT_OF_BOUNDS'}' "
        error_msg += f"(type: {type(dates[i-1]) if i-1 < len(dates) else 'N/A'}), "
        error_msg += f"period_index={i}, dates_length={len(dates)}, "
        error_msg += f"original_error: {str(e)}"
        raise ValueError(error_msg)
    
    stock_from_arrivals, new_transit, transit_arrivals = _process_transit_orders_complete(
        transit_orders, key, current_date, previous_date
    )
    
    # Vectorized inventory updates - EXACTLY like future_reorder_optimized line 475-482
    future_stock = max(0, previous_stock + stock_from_arrivals)
    df['FutureInventory'] = _format_value_complete(future_stock, 'FutureInventory', integer)
    df['FutureTransit'] = _format_value_complete(new_transit, 'FutureTransit', integer)
    df['FutureInventoryTransit'] = _format_value_complete(
        future_stock + new_transit, 'FutureInventoryTransit', integer
    )
    df['TransitArrival'] = str(transit_arrivals) if transit_arrivals else '[]'
    
    # Vectorized reorder calculations - EXACTLY like future_reorder_optimized line 484-508
    df['SecurityStock'] = _calculate_security_stock_complete(df, security_stock_ref, integer)
    df['SuggestedForecast'] = _format_value_complete(df['SuggestedForecast'].iloc[0], 'SuggestedForecast', integer)
    df['ReorderPoint'] = _format_value_complete(
        max(0, df['SuggestedForecast'].iloc[0] + df['SecurityStock'].iloc[0]), 'ReorderPoint', integer
    )
    df['ReorderQtyBase'] = _format_value_complete(
        max(0, df['ReorderPoint'].iloc[0] - df['FutureInventoryTransit'].iloc[0]), 'ReorderQtyBase', integer
    )
    
    # Calculate ReorderQty - EXACTLY like future_reorder_optimized line 494-500
    reorder_qty_base = df['ReorderQtyBase'].iloc[0]
    purchase_factor = df['PurchaseFactor'].iloc[0]
    
    if reorder_qty_base > 0:
        reorder_qty = np.ceil(reorder_qty_base / purchase_factor) * purchase_factor
    else:
        reorder_qty = 0
    
    df['ReorderQty'] = _format_value_complete(reorder_qty, 'ReorderQty', integer)
    
    # Calculate ReorderQtyDays - EXACTLY like future_reorder_optimized line 502-508
    if df['ReorderQty'].iloc[0] > 0 and df['AvgDailyUsage'].iloc[0] > 0:
        reorder_qty_days = df['ReorderQty'].iloc[0] / df['AvgDailyUsage'].iloc[0]
    else:
        reorder_qty_days = 0
    
    df['ReorderQtyDays'] = _format_value_complete(reorder_qty_days, 'ReorderQtyDays', integer)
    
    # Handle new orders - EXACTLY like future_reorder_optimized line 510-521
    if df['ReorderQty'].iloc[0] > 0:
        avg_lead_time = df['AvgLeadTime'].iloc[0]
        arrival_date = current_date + timedelta(days=int(avg_lead_time))
        transit_orders[key].append({
            'quantity': float(df['ReorderQty'].iloc[0]),
            'arrival_date': arrival_date
        })
        df['ArrivalDate'] = arrival_date.strftime('%Y-%m-%d')
    else:
        df['ArrivalDate'] = ''
    
    return df


class FutureReorder():
    """
    Versión completa optimizada para procesamiento masivo de datasets grandes.
    Incluye TODA la funcionalidad de la clase original pero optimizada para paralelización.
    
    Nueva funcionalidad period2:
    - period2 controla el número de períodos para ítems con ReorderFreq <= 20
    - periods controla el número de períodos para ítems con ReorderFreq > 20
    - Esto permite reducir el número de resultados para ítems con frecuencias de reorden pequeñas
    """

    def __init__(self, df_inv, df_lead_time, df_prep, df_fcst, periods, start_date,
                 location=False, security_stock_ref=False, df_transit=None, integer=True,
                 complete_suggested=False, start_date_zero=None, batch_size=None, n_workers=None,
                 verbose=True, period2=2):
        """
        Initialize FutureReorder with enhanced period control.
        
        Args:
            df_inv: Inventory DataFrame
            df_lead_time: Lead time DataFrame
            df_prep: Preparation DataFrame
            df_fcst: Forecast DataFrame
            periods: Number of periods for items with ReorderFreq > 20
            start_date: Start date for calculations
            location: Boolean for location-based processing
            security_stock_ref: Boolean for reference-based security stock
            df_transit: Transit DataFrame (optional)
            integer: Boolean for integer formatting
            complete_suggested: Boolean for complete suggested forecast mode
            start_date_zero: Custom start date for period 0
            batch_size: Batch size for parallel processing (auto-configured if None)
            n_workers: Number of workers for parallel processing (auto-configured if None)
            verbose: Boolean for detailed logging
            period2: Number of periods for items with ReorderFreq <= 20 (default: 2)
        """
        
        # Original parameters - TODOS los parámetros de la clase original
        self.df_inv = df_inv
        self.df_lead_time = df_lead_time
        self.df_prep = df_prep
        self.df_fcst = df_fcst
        self.default_coverage = 30
        self.periods = periods
        self.period2 = period2
        self.start_date = pd.to_datetime(start_date, format='%Y-%m-%d') if start_date is not None else None
        self.location = location
        self.security_stock_ref = security_stock_ref
        self.df_transit = df_transit
        self.integer = integer
        self.complete_suggested = complete_suggested
        self.start_date_zero = start_date_zero
        
        # Optimization parameters with intelligent defaults
        total_items = len(df_inv)
        
        # Auto-configure batch_size based on dataset size
        if batch_size is None:
            if total_items <= 500:
                self.batch_size = 50  # Small batches for small datasets
            elif total_items <= 2000:
                self.batch_size = 100  # Medium batches
            else:
                self.batch_size = 200  # Larger batches for big datasets
        else:
            self.batch_size = batch_size
            
        # Auto-configure n_workers based on system and dataset
        if n_workers is None:
            available_cores = cpu_count()
            if total_items <= 200:
                self.n_workers = min(2, available_cores - 1)  # Conservative for small datasets
            elif total_items <= 1000:
                self.n_workers = min(4, available_cores - 1)  # Moderate parallelization
            else:
                self.n_workers = min(max(4, available_cores - 2), 8)  # Aggressive for large datasets
        else:
            self.n_workers = n_workers
            
        self.verbose = verbose
        
        # Initialize metadata columns
        self.metadata = ['Item']
        if self.location:
            self.metadata.append('Location')
        
        # Pre-filter dataframes based on df_inv to improve performance
        self._prefilter_dataframes()
        
        self._log(f"🚀 FutureReorder Massive Complete - Inicializado para {len(self.df_inv)} ítems")
        self._log(f"⚙️  Configuración: batch_size={batch_size}, workers={self.n_workers}")

    def _prefilter_dataframes(self):
        """
        Pre-filter all input dataframes based on df_inv to improve performance.
        Only process data that exists in df_inv (inventory data).
        """
        if self.verbose:
            original_sizes = {
                'df_lead_time': len(self.df_lead_time),
                'df_prep': len(self.df_prep),
                'df_fcst': len(self.df_fcst),
                'df_transit': len(self.df_transit) if self.df_transit is not None else 0
            }
            self._log("📊 Pre-filtering dataframes based on df_inv...")
        
        # Create base filter from df_inv
        if self.location:
            base_filter = self.df_inv[['Item', 'Location']].drop_duplicates()
        else:
            base_filter = self.df_inv[['Item']].drop_duplicates()
        
        # Filter df_lead_time
        if self.location:
            self.df_lead_time = self.df_lead_time.merge(
                base_filter,
                on=['Item', 'Location'],
                how='inner'
            )
        else:
            self.df_lead_time = self.df_lead_time.merge(
                base_filter,
                on=['Item'],
                how='inner'
            )
        
        # Filter df_prep - handle different column naming conventions
        if self.location:
            # Check if df_prep uses 'item_id' and 'location' columns
            if 'item_id' in self.df_prep.columns and 'location' in self.df_prep.columns:
                # Create renamed base filter for df_prep
                base_filter_prep = base_filter.copy()
                base_filter_prep = base_filter_prep.rename(columns={'Item': 'item_id', 'Location': 'location'})
                self.df_prep = self.df_prep.merge(
                    base_filter_prep,
                    on=['item_id', 'location'],
                    how='inner'
                )
            else:
                # Use standard column names
                self.df_prep = self.df_prep.merge(
                    base_filter,
                    on=['Item', 'Location'],
                    how='inner'
                )
        else:
            # Check if df_prep uses 'item_id' column
            if 'item_id' in self.df_prep.columns:
                base_filter_prep = base_filter.copy()
                base_filter_prep = base_filter_prep.rename(columns={'Item': 'item_id'})
                self.df_prep = self.df_prep.merge(
                    base_filter_prep,
                    on=['item_id'],
                    how='inner'
                )
            else:
                self.df_prep = self.df_prep.merge(
                    base_filter,
                    on=['Item'],
                    how='inner'
                )
        
        # Filter df_fcst
        if self.location:
            self.df_fcst = self.df_fcst.merge(
                base_filter,
                on=['Item', 'Location'],
                how='inner'
            )
        else:
            self.df_fcst = self.df_fcst.merge(
                base_filter,
                on=['Item'],
                how='inner'
            )
        
        # Filter df_transit if it exists
        if self.df_transit is not None:
            if self.location:
                self.df_transit = self.df_transit.merge(
                    base_filter,
                    on=['Item', 'Location'],
                    how='inner'
                )
            else:
                self.df_transit = self.df_transit.merge(
                    base_filter,
                    on=['Item'],
                    how='inner'
                )
        
        if self.verbose:
            new_sizes = {
                'df_lead_time': len(self.df_lead_time),
                'df_prep': len(self.df_prep),
                'df_fcst': len(self.df_fcst),
                'df_transit': len(self.df_transit) if self.df_transit is not None else 0
            }
            
            self._log("📊 Filtrado completado:")
            for df_name, original_size in original_sizes.items():
                new_size = new_sizes[df_name]
                if original_size > 0:
                    reduction_pct = ((original_size - new_size) / original_size) * 100
                    self._log(f"   • {df_name}: {original_size:,} → {new_size:,} (-{reduction_pct:.1f}%)")
                else:
                    self._log(f"   • {df_name}: {original_size:,} → {new_size:,}")

    def _log(self, message):
        if self.verbose:
            print(message)
            sys.stdout.flush()

    def future_date(self):
        """
        Generate future reorder dates for each item based on reorder frequency.
        Versión optimizada de la función original.
        """
        # Determine the starting date for period 0 - EXACTLY like future_reorder_optimized line 148-155
        if self.start_date_zero is not None:
            # Use custom start date for period 0
            actual_date = pd.to_datetime(self.start_date_zero, format='%Y-%m-%d')
        else:
            # Use current system date for period 0 (original behavior)
            DOCKER_CONFIG_PATH = os.path.join('/opt/ml/processing/input', 'config.yml')
            utils = Utils(config_file=DOCKER_CONFIG_PATH, logfile='data_io', log_path='output/logs')
            timestamp = utils.set_timestamp()
            actual_date = pd.to_datetime(str(int(float(timestamp[0:8]))), format='%Y%m%d')
        
        # Use periods + 1 internally to calculate one extra period for transit calculations
        # The extra period will be filtered out in the final results
        end_date = actual_date + pd.DateOffset(months=self.periods + 1)
        
        # Handle start_date = None case
        if self.start_date is None:
            # If start_date is None, use actual_date as the base for period 1
            base_start_date = actual_date
        else:
            base_start_date = self.start_date

        # Get unique items with their reorder frequencies
        columns = self.metadata + ['ReorderFreq']
        df_unique = self.df_lead_time[columns].drop_duplicates().copy()
        
        # Process ReorderFreq values
        df_unique['ReorderFreq'] = df_unique['ReorderFreq'].fillna(self.default_coverage)
        df_unique.loc[df_unique['ReorderFreq'] == 0, 'ReorderFreq'] = self.default_coverage
        df_unique['ReorderFreq'] = df_unique['ReorderFreq'].astype(int)
        
        # Pre-allocate result dictionary
        item_dates = {}
        
        # Group by ReorderFreq for batch processing - more efficient for large datasets
        for freq, group in df_unique.groupby('ReorderFreq'):
            # Generate date range for this frequency
            date_range = []
            
            # Always include actual date (period 0)
            date_range.append(actual_date)
            
            # Include base_start_date if after actual_date
            if base_start_date > actual_date:
                date_range.append(base_start_date)
            
            # Generate subsequent dates using pandas date_range for efficiency
            num_periods = int((end_date - base_start_date).days / freq) + 1
            future_dates = pd.date_range(
                start=base_start_date + timedelta(days=freq),
                periods=num_periods,
                freq=f'{freq}D'
            )
            date_range.extend(future_dates[future_dates <= end_date])
            
            # Convert to string format
            date_strings = [d.strftime('%Y%m%d') for d in date_range]
            
            # Assign to all items in this group
            for _, row in group.iterrows():
                if self.location:
                    key = (row['Item'], row['Location'])
                else:
                    key = row['Item']
                item_dates[key] = date_strings
        
        return item_dates

    def _prepare_batch_data(self):
        """
        Prepara datos por lotes de manera eficiente sin generar fechas pre-calculadas.
        Las fechas se generarán localmente en cada worker process.
        """
        batch_data = []
        
        # Get unique items from df_inv
        if self.location:
            unique_items = self.df_inv[['Item', 'Location']].drop_duplicates()
        else:
            unique_items = self.df_inv[['Item']].drop_duplicates()
        
        for _, row in unique_items.iterrows():
            try:
                if self.location:
                    key = (row['Item'], row['Location'])
                    item, location = key
                else:
                    key = row['Item']
                    item = key
                    location = None
                    
                # Create filter mask based on item
                mask_lead_time = self.df_lead_time['Item'] == item
                mask_inv = self.df_inv['Item'] == item
                
                # Add location filter if needed
                if self.location and location is not None:
                    mask_lead_time &= self.df_lead_time['Location'] == location
                    mask_inv &= self.df_inv['Location'] == location
                
                # Apply filters using boolean indexing
                current_df_lead_time = self.df_lead_time[mask_lead_time]
                current_df_inv = self.df_inv[mask_inv]
                
                if not current_df_lead_time.empty and not current_df_inv.empty:
                    # Only include key and dataframes, dates will be generated in worker
                    batch_data.append((key, current_df_lead_time, current_df_inv))
                    
            except Exception as e:
                if self.verbose:
                    print(f"Error preparando {key}: {e}")
                continue
        
        return batch_data

    def _prepare_final_dataframe(self, data_frame):
        """
        Prepare the final output dataframe with proper formatting and column selection.
        Versión completa de la función original.
        """
        leadtimes_columns = ['Item', 'Location', 'ReorderFreq', 'Coverage'] if self.location else ['Item', 'ReorderFreq', 'Coverage']
        leadtimes = self.df_lead_time[leadtimes_columns]
        df_final = pd.merge(data_frame, leadtimes, on=self.metadata, how='left').fillna(0)
        
        # Format date and rename to PurchaseDate
        df_final['PurchaseDate'] = pd.to_datetime(df_final['Date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
        df_final = df_final.drop('Date', axis=1)
        
        # Ensure ArrivalDate is present (in case some records don't have it)
        if 'ArrivalDate' not in df_final.columns:
            df_final['ArrivalDate'] = ''
        
        # Apply formatting to fields that are ALWAYS integers
        always_integer_fields = ['PurchaseFactor', 'AvgLeadTime', 'MaxLeadTime', 'ReorderQtyDays', 'ReorderFreq', 'Coverage']
        for field in always_integer_fields:
            if field in df_final.columns:
                df_final[field] = df_final[field].apply(lambda x: _format_value_complete(x, field, True))
        
        # Apply formatting to fields that are ALWAYS decimals
        always_decimal_fields = ['AvgDailyUsage', 'MaxDailyUsage']
        for field in always_decimal_fields:
            if field in df_final.columns:
                df_final[field] = df_final[field].apply(lambda x: _format_value_complete(x, field, False))
        
        # Select final columns
        if self.location:
            final_cols = [
                'PurchaseDate', 'Item', 'ItemDescription', 'Location', 'SuggestedForecast',
                'SuggestedForecastPeriod', 'FutureInventoryTransit', 'FutureInventory',
                'FutureTransit', 'FutureInventoryTransitArrival', 'FutureStockoutDays', 'TransitArrival',
                'ReorderQtyBase', 'ReorderQty', 'ReorderQtyDays', 'ArrivalDate', 'PurchaseFactor',
                'ReorderPoint', 'SecurityStock', 'AvgDailyUsage', 'MaxDailyUsage', 'AvgLeadTime',
                'MaxLeadTime', 'ReorderFreq', 'Coverage'
            ]
        else:
            final_cols = [
                'PurchaseDate', 'Item', 'ItemDescription', 'SuggestedForecast',
                'SuggestedForecastPeriod', 'FutureInventoryTransit', 'FutureInventory',
                'FutureTransit', 'FutureInventoryTransitArrival', 'FutureStockoutDays', 'TransitArrival',
                'ReorderQtyBase', 'ReorderQty', 'ReorderQtyDays', 'ArrivalDate', 'PurchaseFactor',
                'ReorderPoint', 'SecurityStock', 'AvgDailyUsage', 'MaxDailyUsage', 'AvgLeadTime',
                'MaxLeadTime', 'ReorderFreq', 'Coverage'
            ]
        
        return df_final[final_cols]

    def _filter_periods(self, df):
        """
        Filter out period 0 and last period from results.
        Period 0 is used only as calculation base.
        Last period is filtered because it doesn't have next period transit data.
        
        Special case: When start_date=None, don't filter the first period
        because it represents the actual current period.
        """
        if df.empty:
            return df
        
        # Convert PurchaseDate to datetime for filtering
        df['PurchaseDate_dt'] = pd.to_datetime(df['PurchaseDate'])
        
        # Get unique dates and sort them
        unique_dates = sorted(df['PurchaseDate_dt'].unique())
        
        # Determine filtering logic based on start_date parameter
        if self.start_date is None:
            # When start_date=None, only filter the last period
            # Keep period 0 as it represents the current period
            if len(unique_dates) <= 1:
                self._log("⚠️  Warning: Only 1 period available, cannot filter last period")
                return pd.DataFrame(columns=df.columns.drop('PurchaseDate_dt'))
            
            last_date = unique_dates[-1]
            filtered_df = df[df['PurchaseDate_dt'] != last_date].copy()
            
            self._log(f"📊 Filtered periods (start_date=None): Only removed last period ({last_date.strftime('%Y-%m-%d')})")
            
        else:
            # When start_date is specified, filter both first and last periods (original logic)
            if len(unique_dates) <= 2:
                self._log("⚠️  Warning: Only 2 or fewer periods available after filtering")
                return pd.DataFrame(columns=df.columns.drop('PurchaseDate_dt'))
            
            first_date = unique_dates[0]
            last_date = unique_dates[-1]
            
            filtered_df = df[
                (df['PurchaseDate_dt'] != first_date) &
                (df['PurchaseDate_dt'] != last_date)
            ].copy()
            
            self._log(f"📊 Filtered periods: Removed period 0 ({first_date.strftime('%Y-%m-%d')}) and last period ({last_date.strftime('%Y-%m-%d')})")
        
        # Drop the temporary datetime column
        filtered_df = filtered_df.drop('PurchaseDate_dt', axis=1)
        
        return filtered_df

    def reorder(self):
        """
        Main method to calculate future reorder recommendations at massive scale.
        
        This high-performance method orchestrates the complete inventory reorder calculation
        process using parallel processing and intelligent resource management. It handles
        large datasets efficiently through batching, multiprocessing, and optimized algorithms.
        
        Processing Pipeline:
        1. Generate future dates based on reorder frequencies and period control
        2. Pre-filter and prepare data for batch processing
        3. Split items into optimally-sized batches
        4. Process batches in parallel using multiple CPU cores
        5. Combine and format results with proper data types
        6. Apply period filtering (removes period 0 and last period)
        7. Return comprehensive reorder recommendations
        
        Performance Features:
        - Auto-configures batch sizes based on dataset size
        - Uses ProcessPoolExecutor for true parallel processing
        - Provides real-time progress tracking and ETA calculations
        - Implements intelligent error handling and recovery
        - Optimizes memory usage through efficient data structures
        
        Period Control Logic:
        - Items with ReorderFreq <= 20: Uses period2 (default: 2 periods)
        - Items with ReorderFreq > 20: Uses periods parameter
        - This reduces output volume for high-frequency reorder items
        
        Period Filtering Logic:
        - When start_date=None: Only removes last period (keeps period 0 as current)
        - When start_date specified: Removes both period 0 and last period
        - Last period is always removed due to incomplete transit data
        
        Returns:
            pd.DataFrame: Complete reorder recommendations with columns:
                - PurchaseDate: Date when reorder should be evaluated
                - Item, ItemDescription, (Location): Item identification
                - Forecast metrics: SuggestedForecast, SuggestedForecastPeriod
                - Inventory levels: FutureInventoryTransit, FutureInventory, FutureTransit
                - FutureInventoryTransitArrival: Stock + arrivals in the period
                - FutureStockoutDays: Days of inventory coverage
                - Transit information: TransitArrival details
                - Reorder metrics: ReorderQtyBase, ReorderQty, ReorderQtyDays
                - Order information: ArrivalDate of current period's order
                - Planning parameters: PurchaseFactor, ReorderPoint, SecurityStock
                - Usage rates: AvgDailyUsage, MaxDailyUsage
                - Lead times: AvgLeadTime, MaxLeadTime
                - Coverage parameters: ReorderFreq, Coverage
                
        Example usage:
            >>> reorder_system = FutureReorder(
            ...     df_inv=inventory_df,
            ...     df_lead_time=lead_time_df,
            ...     df_prep=prep_df,
            ...     df_fcst=forecast_df,
            ...     periods=6,        # For items with ReorderFreq > 20
            ...     start_date=None,  # Use current date
            ...     period2=2,        # For items with ReorderFreq <= 20
            ...     batch_size=100,   # Optional: auto-configured if None
            ...     n_workers=4       # Optional: auto-configured if None
            ... )
            >>> results = reorder_system.reorder()
            >>> print(f"Generated {len(results)} reorder recommendations")
        """
        start_time = time.time()
        
        self._log("🚀 FutureReorder Massive Complete - Processing Started")
        
        # Prepare batch data without pre-generating dates
        self._log("🔧 Preparando datos por lotes...")
        batch_data = self._prepare_batch_data()
        
        # Calculate statistics based on items that will be processed
        total_items = len(batch_data)
        
        self._log(f"📊 Dataset Info:")
        self._log(f"   • Total Items: {total_items}")
        self._log(f"   • Periods (ReorderFreq > 20): {self.periods}")
        self._log(f"   • Period2 (ReorderFreq <= 20): {self.period2}")
        self._log(f"   • Estimated Total Calculations: {total_items * self.periods}")
        
        if not batch_data:
            self._log("⚠️  No items to process after filtering")
            columns = ['Date', 'Item'] + (['Location'] if self.location else [])
            return pd.DataFrame(columns=columns)
        
        # Split into batches for parallel processing
        batches = []
        for i in range(0, len(batch_data), self.batch_size):
            batch = batch_data[i:i + self.batch_size]
            batch_args = (
                batch, self.df_fcst, self.df_prep, self.metadata,
                self.location, self.default_coverage, self.complete_suggested,
                self.security_stock_ref, self.integer, self.verbose, self.df_transit,
                self.periods, self.period2, self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
                self.start_date_zero
            )
            batches.append(batch_args)
        
        total_batches = len(batches)
        items_per_batch = len(batch_data) / total_batches if total_batches > 0 else 0
        
        self._log(f"⚙️  Processing Config:")
        self._log(f"   • Batch Size: {self.batch_size}")
        self._log(f"   • Workers: {self.n_workers}")
        self._log(f"   • Total Batches: {total_batches}")
        self._log(f"   • Items per Batch: {items_per_batch:.1f}")
        
        current_time = datetime.now().strftime('%H:%M:%S')
        self._log(f"⏱️  Starting processing at {current_time}")
        
        # Process batches in parallel
        results = []
        completed_batches = 0
        
        with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
            # Submit all batches
            future_to_batch = {executor.submit(process_item_batch_complete, batch_args): i 
                             for i, batch_args in enumerate(batches)}
            
            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                try:
                    result = future.result()
                    if not result.empty:
                        results.append(result)
                    
                    completed_batches += 1
                    progress = (completed_batches / total_batches) * 100
                    
                    elapsed_time = time.time() - start_time
                    if completed_batches > 0:
                        eta_seconds = (elapsed_time / completed_batches) * (total_batches - completed_batches)
                        eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
                    else:
                        eta_str = "calculating..."
                    
                    self._log(f"✅ Batch {completed_batches}/{total_batches} completed ({progress:.1f}%) - ETA: {eta_str}")
                    
                except Exception as e:
                    self._log(f"❌ Error in batch {batch_idx}: {e}")
                    continue
        
        # Combine all results
        if results:
            self._log("🔗 Combinando resultados...")
            final_result = pd.concat(results, ignore_index=True)
            
            # Prepare final dataframe with proper formatting
            final_result = self._prepare_final_dataframe(final_result)
            
            # Filter out period 0 and last period from results
            final_result = self._filter_periods(final_result)
            
            total_time = time.time() - start_time
            self._log(f"🎉 Processing completed in {total_time:.2f}s")
            self._log(f"📈 Final result: {len(final_result)} records")
            
            return final_result
        else:
            self._log("⚠️  No results generated")
            columns = ['Date', 'Item'] + (['Location'] if self.location else [])
            return pd.DataFrame(columns=columns)