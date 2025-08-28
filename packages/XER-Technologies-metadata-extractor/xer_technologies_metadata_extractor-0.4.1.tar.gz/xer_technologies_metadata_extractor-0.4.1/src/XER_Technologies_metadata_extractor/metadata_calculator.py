"""
Metadata Calculator Module

This module calculates metadata values based on the configuration.
It provides a flexible system for extracting different types of metadata.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .metadata_config import MetadataField, metadata_config
from .postprocessing_integration import postprocessing_integration


class MetadataCalculator:
    """Calculates metadata values based on configuration."""
    
    def __init__(self, config=None):
        """
        Initialize the metadata calculator.
        
        Args:
            config: MetadataConfig instance (uses default if None)
        """
        self.config = config or metadata_config
    
    def calculate_metadata(self, df: pd.DataFrame, filename: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Calculate all configured metadata values.
        
        Args:
            df: Processed DataFrame
            filename: Original filename
            verbose: Whether to print detailed information
            
        Returns:
            Dictionary with all calculated metadata
        """
        if verbose:
            print("📊 Calculating metadata values...")
        
        metadata = {}
        
        # Process DataFrame through postprocessing pipeline
        processed_df, post_processing_stats = postprocessing_integration.process_dataframe(df, verbose)
        
        # Store post-processing stats for warning messages
        self._post_processing_stats = post_processing_stats
        
        # Add post-processing metadata
        metadata["post_processing"] = post_processing_stats
        
        # Calculate metadata for each field in configuration
        for field in self.config.fields:
            try:
                value = self._calculate_field_value(field, processed_df, filename, verbose)
                if value is not None:
                    metadata[field.name] = value
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Error calculating {field.name}: {str(e)}")
                # Don't add failed fields to metadata
        
        # Add dynamic statistics for all columns with sufficient data
        dynamic_stats = self._calculate_dynamic_statistics(processed_df, verbose)
        metadata.update(dynamic_stats)
        
        # Add validation results
        validation_results = postprocessing_integration.validate_data_quality(processed_df)
        metadata["validation_results"] = validation_results
        
        if verbose:
            print(f"   ✓ Calculated {len(metadata)} metadata fields")
        
        return metadata
    
    def _calculate_field_value(self, field: MetadataField, df: pd.DataFrame, filename: str, verbose: bool = False) -> Optional[Any]:
        """
        Calculate a single field value.
        
        Args:
            field: MetadataField configuration
            df: Processed DataFrame
            filename: Original filename
            verbose: Whether to print detailed information
            
        Returns:
            Calculated value or None if calculation fails
        """
        # Find the source column for this field (skip for fields that don't need source columns)
        if field.calculation_method in ["file_type"]:
            source_column = "dummy"  # Dummy value for fields that don't need source columns
        else:
            source_column = self._find_source_column(field, df)
            if source_column is None:
                if verbose and field.required:
                    print(f"   ⚠️  Missing required column for {field.name}")
                return None
        
        if verbose:
            print(f"   📈 Calculating {field.name} from {source_column}")
        
        # Calculate based on method
        if field.calculation_method == "max":
            return self._calculate_max(df, source_column)
        elif field.calculation_method == "min":
            return self._calculate_min(df, source_column)
        elif field.calculation_method == "avg":
            return self._calculate_avg(df, source_column)
        elif field.calculation_method == "first":
            return self._calculate_first(df, source_column)
        elif field.calculation_method == "last":
            return self._calculate_last(df, source_column)
        elif field.calculation_method == "duration":
            return self._calculate_duration(df, source_column)
        elif field.calculation_method == "duration_conditional":
            return self._calculate_duration_conditional(df, field, source_column)
        elif field.calculation_method == "engine_starts":
            return self._calculate_engine_starts(df, source_column)
        elif field.calculation_method == "engine_hours":
            return self._calculate_engine_hours(df, source_column)
        elif field.calculation_method == "flight_hours":
            return self._calculate_flight_hours(df, source_column)
        elif field.calculation_method == "row_count":
            return len(df)
        # elif field.calculation_method == "data_points":
        #     return len(df)
        elif field.calculation_method == "date_from_time":
            return self._extract_date_from_time_column(df, field.source_columns)
        elif field.calculation_method == "serial_number":
            return self._extract_serial_number_from_data(df)
        elif field.calculation_method == "file_type":
            return "csv"
        elif field.calculation_method == "timestamp":
            return self._extract_timestamp_from_data(df)
        else:
            if verbose:
                print(f"   ⚠️  Unknown calculation method: {field.calculation_method}")
            return None
    
    def _find_source_column(self, field: MetadataField, df: pd.DataFrame) -> Optional[str]:
        """Find the appropriate source column for a field."""
        if not field.source_columns:
            return None
        
        for col_name in field.source_columns:
            if col_name in df.columns:
                return col_name
        
        # Column not found - add warning to post-processing stats
        missing_columns = ", ".join(field.source_columns)
        warning_msg = f"Could not calculate {field.name} as column(s) {missing_columns} was not present. {field.name} was set to NaN"
        
        # Add warning to post-processing stats if available
        if hasattr(self, '_post_processing_stats'):
            if 'warnings' not in self._post_processing_stats:
                self._post_processing_stats['warnings'] = []
            self._post_processing_stats['warnings'].append(warning_msg)
        
        return None
    
    def _calculate_max(self, df: pd.DataFrame, column: str) -> Optional[float]:
        """Calculate maximum value of a column during flight only."""
        if column not in df.columns:
            return None
        try:
            # Filter to only include data when drone is in flight
            flight_mask = df.get('droneInFlight', pd.Series([1] * len(df))) == 1
            flight_data = df[flight_mask]
            
            if len(flight_data) == 0:
                return None
                
            values = pd.to_numeric(flight_data[column], errors='coerce')
            if not values.isna().all():
                return float(values.max())
        except:
            pass
        return None
    
    def _calculate_min(self, df: pd.DataFrame, column: str) -> Optional[float]:
        """Calculate minimum value of a column during flight only."""
        if column not in df.columns:
            return None
        try:
            # Filter to only include data when drone is in flight
            flight_mask = df.get('droneInFlight', pd.Series([1] * len(df))) == 1
            flight_data = df[flight_mask]
            
            if len(flight_data) == 0:
                return None
                
            values = pd.to_numeric(flight_data[column], errors='coerce')
            if not values.isna().all():
                return float(values.min())
        except:
            pass
        return None
    
    def _calculate_avg(self, df: pd.DataFrame, column: str) -> Optional[float]:
        """Calculate average value of a column during flight only."""
        if column not in df.columns:
            return None
        try:
            # Filter to only include data when drone is in flight
            flight_mask = df.get('droneInFlight', pd.Series([1] * len(df))) == 1
            flight_data = df[flight_mask]
            
            if len(flight_data) == 0:
                return None
                
            values = pd.to_numeric(flight_data[column], errors='coerce')
            if not values.isna().all():
                return float(values.mean())
        except:
            pass
        return None
    
    def _calculate_first(self, df: pd.DataFrame, column: str) -> Optional[str]:
        """Get first value of a column."""
        try:
            if column in df.columns and len(df) > 0:
                first_value = df[column].iloc[0]
                if pd.notna(first_value):
                    # If it's a timestamp column, format as HH:MM:SS
                    if column.lower() in ['time', 'timestamp']:
                        timestamps = self._parse_timestamps(df[column])
                        if not timestamps.isna().all():
                            first_timestamp = timestamps.dropna().iloc[0]
                            return first_timestamp.strftime('%H:%M:%S')
                    return str(first_value)
        except:
            pass
        return None
    
    def _calculate_last(self, df: pd.DataFrame, column: str) -> Optional[str]:
        """Get last value of a column."""
        try:
            if column in df.columns and len(df) > 0:
                last_value = df[column].iloc[-1]
                if pd.notna(last_value):
                    # If it's a timestamp column, format as HH:MM:SS
                    if column.lower() in ['time', 'timestamp']:
                        timestamps = self._parse_timestamps(df[column])
                        if not timestamps.isna().all():
                            last_timestamp = timestamps.dropna().iloc[-1]
                            return last_timestamp.strftime('%H:%M:%S')
                    return str(last_value)
        except:
            pass
        return None
    
    def _calculate_duration(self, df: pd.DataFrame, column: str) -> Optional[str]:
        """Calculate duration from timestamp column."""
        try:
            if column in df.columns and len(df) > 0:
                # Try to parse timestamps - handle Unix timestamps in milliseconds
                timestamps = self._parse_timestamps(df[column])
                if not timestamps.isna().all():
                    start_time = timestamps.min()
                    end_time = timestamps.max()
                    duration = end_time - start_time
                    return self._format_duration(duration)
        except:
            pass
        return None
    
    def _calculate_duration_conditional(self, df: pd.DataFrame, field: MetadataField, column: str) -> Optional[str]:
        """Calculate duration when a condition is met."""
        try:
            if column in df.columns and len(df) > 0:
                # Get the condition from validation rules
                condition = field.validation_rules.get("condition", "")
                if condition:
                    # Parse condition (e.g., "isGeneratorRunning == 1")
                    if "isGeneratorRunning" in condition and "==" in condition:
                        value = int(condition.split("==")[1].strip())
                        if "isGeneratorRunning" in df.columns:
                            # Filter rows where condition is met
                            condition_met = df["isGeneratorRunning"] == value
                            if condition_met.any():
                                # Get timestamps for rows where condition is met
                                time_column = self._find_time_column(df)
                                if time_column:
                                    timestamps = self._parse_timestamps(df[time_column])
                                    condition_timestamps = timestamps[condition_met]
                                    if not condition_timestamps.isna().all():
                                        start_time = condition_timestamps.min()
                                        end_time = condition_timestamps.max()
                                        duration = end_time - start_time
                                        return self._format_duration(duration)
                            else:
                                # Condition never met, return zero duration
                                return "00:00:00"
        except:
            pass
        return "00:00:00"
    
    def _calculate_engine_starts(self, df: pd.DataFrame, column: str) -> Optional[int]:
        """Calculate number of engine starts using isGeneratorRunning column."""
        try:
            if column in df.columns:
                # Count transitions from 0 to 1 in isGeneratorRunning column
                starts = (df[column] == 1) & (df[column].shift(1) == 0)
                return int(starts.sum())
        except:
            pass
        return None
    
    def _calculate_engine_hours(self, df: pd.DataFrame, column: str) -> Optional[float]:
        """Calculate engine working hours using isGeneratorRunning column."""
        try:
            if column in df.columns:
                # Use isGeneratorRunning column directly
                engine_running = df[column] == 1
                
                # Get time column for duration calculation
                time_column = self._find_time_column(df)
                if time_column:
                    timestamps = self._parse_timestamps(df[time_column])
                    if not timestamps.isna().all():
                        # Calculate total time when engine is running
                        running_timestamps = timestamps[engine_running]
                        if len(running_timestamps) > 1:
                            total_time = running_timestamps.max() - running_timestamps.min()
                            return total_time.total_seconds() / 3600  # Convert to hours
                        else:
                            # No engine running time, return 0 hours
                            return 0.0
        except:
            pass
        return 0.0
    
    def _calculate_flight_hours(self, df: pd.DataFrame, column: str) -> Optional[float]:
        """Calculate total flight hours using droneInFlight column."""
        try:
            if column in df.columns:
                # Use droneInFlight column directly
                flight_active = df[column] == 1
                
                # Get time column for duration calculation
                time_column = self._find_time_column(df)
                if time_column:
                    timestamps = self._parse_timestamps(df[time_column])
                    if not timestamps.isna().all():
                        # Calculate total time when flight is active
                        active_timestamps = timestamps[flight_active]
                        if len(active_timestamps) > 1:
                            total_time = active_timestamps.max() - active_timestamps.min()
                            return total_time.total_seconds() / 3600  # Convert to hours
                        else:
                            # No flight time, return 0 hours
                            return 0.0
        except:
            pass
        return 0.0


    
    def _extract_serial_number_from_data(self, df: pd.DataFrame) -> Optional[str]:
        """Extract serial number from CSV data."""
        # Look for serial number in common column names
        serial_columns = [col for col in df.columns if 'serial' in col.lower() or 'sn' in col.lower()]
        if serial_columns:
            for col in serial_columns:
                values = df[col].dropna()
                if len(values) > 0:
                    # Find the first value that has exactly 3 digits
                    for value in values:
                        str_value = str(int(value))  # Convert to int to remove decimals, then to string
                        if len(str_value) == 3:
                            return str_value
        return None
    
    def _extract_flight_date_from_data(self, df: pd.DataFrame) -> Optional[str]:
        """Extract flight date from CSV data."""
        # Look for date in timestamp columns
        time_columns = [col for col in df.columns if col.lower() in ['time', 'timestamp', 'datetime']]
        for col in time_columns:
            try:
                # Try to parse timestamps and extract date
                timestamps = self._parse_timestamps(df[col])
                if not timestamps.isna().all():
                    # Get the first valid timestamp
                    first_timestamp = timestamps.dropna().iloc[0]
                    return first_timestamp.strftime('%Y-%m-%d')
            except:
                continue
        return None
    
    def _extract_timestamp_from_data(self, df: pd.DataFrame) -> Optional[str]:
        """Extract timestamp from CSV data."""
        # Look for timestamp in columns
        time_columns = [col for col in df.columns if col.lower() in ['time', 'timestamp', 'datetime']]
        for col in time_columns:
            try:
                # Try to parse timestamps
                timestamps = self._parse_timestamps(df[col])
                if not timestamps.isna().all():
                    # Get the first valid timestamp
                    first_timestamp = timestamps.dropna().iloc[0]
                    return first_timestamp.isoformat()
            except:
                continue
        return None
    
    def _extract_date_from_time_column(self, df: pd.DataFrame, source_columns: List[str]) -> Optional[str]:
        """Extract date from time column in CSV data."""
        for col in source_columns:
            if col in df.columns:
                try:
                    # Try to parse timestamps and extract date
                    timestamps = self._parse_timestamps(df[col])
                    if not timestamps.isna().all():
                        # Get the first valid timestamp
                        first_timestamp = timestamps.dropna().iloc[0]
                        return first_timestamp.strftime('%Y-%m-%d')
                except:
                    continue
        return None
    
    def _find_rpm_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find RPM column in DataFrame."""
        rpm_columns = [col for col in df.columns if "rpm" in col.lower()]
        return rpm_columns[0] if rpm_columns else None
    
    def _find_time_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find time column in DataFrame."""
        time_columns = [col for col in df.columns if col.lower() in ["time", "timestamp"]]
        return time_columns[0] if time_columns else None
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration as HH:MM:SS."""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _calculate_dynamic_statistics(self, df: pd.DataFrame, verbose: bool = False) -> Dict[str, Any]:
        """
        Calculate dynamic statistics for all columns with sufficient data.
        
        Args:
            df: Processed DataFrame
            verbose: Whether to print detailed information
            
        Returns:
            Dictionary with dynamic statistics
        """
        dynamic_stats = {}
        
        # Filter to only include data when drone is in flight
        flight_mask = df.get('droneInFlight', pd.Series([1] * len(df))) == 1
        flight_data = df[flight_mask]
        
        if len(flight_data) == 0:
            if verbose:
                print("   ⚠️  No flight data available for dynamic statistics")
            return dynamic_stats
        
        # Minimum rows required for statistics
        MIN_ROWS = 10
        
        # Columns to exclude from dynamic statistics
        exclude_columns = {
            'time', 'timestamp', 'datetime',  # Time columns
            'isGeneratorRunning', 'droneInFlight',  # Status columns
            'SN', 'serial',  # Serial number columns
            'FW', 'run_time',  # Firmware version columns
        }
        
        # Get list of columns already handled by configuration
        configured_columns = set()
        for field in self.config.fields:
            if field.source_columns:
                configured_columns.update(field.source_columns)
        
        # Add configured columns to exclude list
        exclude_columns.update(configured_columns)
        
        for column in df.columns:
            # Skip excluded columns
            if column.lower() in exclude_columns or any(exclude in column.lower() for exclude in exclude_columns):
                continue
                
            # Get flight data for this column
            column_data = flight_data[column]
            
            # Convert to numeric, ignoring errors
            numeric_data = pd.to_numeric(column_data, errors='coerce')
            
            # Check if we have enough valid numeric data
            valid_data = numeric_data.dropna()
            if len(valid_data) < MIN_ROWS:
                continue
                
            # Calculate statistics
            try:
                # Average
                avg_value = float(valid_data.mean())
                dynamic_stats[f"avg_{column.lower()}"] = avg_value
                
                # Maximum
                max_value = float(valid_data.max())
                dynamic_stats[f"max_{column.lower()}"] = max_value
                
                # Standard deviation
                std_value = float(valid_data.std())
                dynamic_stats[f"std_dev_{column.lower()}"] = std_value
                
                if verbose:
                    print(f"   📊 Dynamic stats for {column}: avg={avg_value:.2f}, max={max_value:.2f}, std={std_value:.2f}")
                    
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Error calculating dynamic stats for {column}: {str(e)}")
                continue
        
        if verbose:
            print(f"   ✓ Calculated dynamic statistics for {len(dynamic_stats) // 3} columns")
            
        return dynamic_stats

    def _parse_timestamps(self, column: pd.Series) -> pd.Series:
        """
        Attempt to parse various timestamp formats.
        Handles Unix timestamps in milliseconds (e.g., 1715842214734)
        and standard datetime strings.
        """
        try:
            # Try to parse as Unix timestamp (milliseconds)
            if column.dtype == 'int64':
                return pd.to_datetime(column / 1000, unit='s', errors='coerce')
            # Try to parse as standard datetime strings
            return pd.to_datetime(column, errors='coerce')
        except:
            return pd.Series([np.nan] * len(column), dtype=pd.DatetimeTZDtype(unit='s'))


# Global instance for easy access
metadata_calculator = MetadataCalculator() 