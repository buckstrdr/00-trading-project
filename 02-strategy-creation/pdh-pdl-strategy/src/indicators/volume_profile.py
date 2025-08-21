"""
Volume Profile analysis for PDH/PDL trading strategy.
Implements Point of Control (POC) and High/Low Volume Node identification.
"""

import logging
import pandas as pd
import numpy as np
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class VolumeNode:
    """Individual volume node in the profile."""
    price: Decimal
    volume: int
    percentage: float  # Percentage of total session volume
    bar_count: int    # Number of bars that traded at this price


@dataclass
class HighVolumeNode(VolumeNode):
    """High Volume Node - significant volume concentration."""
    significance: float  # How significant this HVN is (0.0 - 1.0)
    support_resistance_strength: float  # Likelihood of acting as S/R
    
    def is_strong_support_resistance(self) -> bool:
        """Check if this HVN is likely strong support/resistance."""
        return self.support_resistance_strength > 0.7


@dataclass
class LowVolumeNode(VolumeNode):
    """Low Volume Node - area of low trading activity."""
    gap_size: float  # Size of the low volume gap
    breakout_potential: float  # Likelihood of fast movement through this area
    
    def is_potential_breakout_zone(self) -> bool:
        """Check if this LVN is potential breakout zone."""
        return self.breakout_potential > 0.6


class POCAnalyzer:
    """Point of Control analyzer."""
    
    @staticmethod
    def find_poc(volume_profile: Dict[Decimal, int]) -> Optional[Decimal]:
        """Find Point of Control (price with highest volume)."""
        if not volume_profile:
            return None
        
        poc_price = max(volume_profile.keys(), key=lambda x: volume_profile[x])
        return poc_price
    
    @staticmethod
    def find_poc_zone(volume_profile: Dict[Decimal, int], 
                      zone_threshold: float = 0.1) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """
        Find POC zone (range around POC with significant volume).
        
        Args:
            volume_profile: Price-volume mapping
            zone_threshold: Percentage threshold for zone inclusion
            
        Returns:
            (zone_low, zone_high) prices
        """
        if not volume_profile:
            return None, None
        
        poc = POCAnalyzer.find_poc(volume_profile)
        if not poc:
            return None, None
        
        max_volume = volume_profile[poc]
        threshold_volume = max_volume * zone_threshold
        
        # Find zone boundaries
        sorted_prices = sorted(volume_profile.keys())
        poc_index = sorted_prices.index(poc)
        
        # Expand down
        zone_low = poc
        for i in range(poc_index - 1, -1, -1):
            price = sorted_prices[i]
            if volume_profile[price] >= threshold_volume:
                zone_low = price
            else:
                break
        
        # Expand up
        zone_high = poc
        for i in range(poc_index + 1, len(sorted_prices)):
            price = sorted_prices[i]
            if volume_profile[price] >= threshold_volume:
                zone_high = price
            else:
                break
        
        return zone_low, zone_high
    
    @staticmethod
    def calculate_poc_distance(current_price: Decimal, poc: Decimal) -> Tuple[Decimal, float]:
        """
        Calculate distance from current price to POC.
        
        Returns:
            (distance, direction) where direction is 1.0 if above POC, -1.0 if below
        """
        distance = abs(current_price - poc)
        direction = 1.0 if current_price > poc else -1.0
        return distance, direction


class VolumeProfile:
    """Volume Profile calculator and analyzer."""
    
    def __init__(self, tick_size: Decimal = Decimal('0.25')):
        """
        Initialize Volume Profile calculator.
        
        Args:
            tick_size: Minimum price increment for the instrument
        """
        self.tick_size = tick_size
        self.volume_profile: Dict[Decimal, int] = {}
        self.total_volume = 0
        self.price_range: Tuple[Optional[Decimal], Optional[Decimal]] = (None, None)
        
    def build_profile(self, data: pd.DataFrame) -> Dict[Decimal, VolumeNode]:
        """
        Build volume profile from market data.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Dictionary mapping price levels to VolumeNode objects
        """
        try:
            if data.empty:
                logger.warning("Empty data provided to volume profile")
                return {}
            
            volume_profile = defaultdict(int)
            bar_count = defaultdict(int)
            
            # Build volume profile by distributing bar volume across price range
            for _, row in data.iterrows():
                high = Decimal(str(row['high']))
                low = Decimal(str(row['low'])) 
                volume = int(row['volume'])
                
                if volume == 0:
                    continue
                
                # Calculate price levels within the bar's range
                price_levels = self._get_price_levels_in_range(low, high)
                
                if not price_levels:
                    continue
                
                # Distribute volume evenly across price levels in the bar
                volume_per_level = volume // len(price_levels)
                remainder = volume % len(price_levels)
                
                for i, price_level in enumerate(price_levels):
                    level_volume = volume_per_level
                    if i < remainder:  # Distribute remainder to first few levels
                        level_volume += 1
                    
                    volume_profile[price_level] += level_volume
                    bar_count[price_level] += 1
            
            # Calculate total volume
            self.total_volume = sum(volume_profile.values())
            self.volume_profile = dict(volume_profile)
            
            # Create VolumeNode objects
            volume_nodes = {}
            for price, volume in volume_profile.items():
                percentage = (volume / self.total_volume * 100) if self.total_volume > 0 else 0
                
                volume_nodes[price] = VolumeNode(
                    price=price,
                    volume=volume,
                    percentage=percentage,
                    bar_count=bar_count[price]
                )
            
            # Update price range
            if volume_profile:
                self.price_range = (min(volume_profile.keys()), max(volume_profile.keys()))
            
            logger.info(f"Built volume profile with {len(volume_nodes)} price levels")
            return volume_nodes
            
        except Exception as e:
            logger.error(f"Error building volume profile: {e}")
            return {}
    
    def _get_price_levels_in_range(self, low: Decimal, high: Decimal) -> List[Decimal]:
        """Get all tick-aligned price levels within a range."""
        price_levels = []
        current_price = self._round_to_tick(low)
        
        while current_price <= high:
            price_levels.append(current_price)
            current_price += self.tick_size
        
        return price_levels
    
    def _round_to_tick(self, price: Decimal) -> Decimal:
        """Round price to nearest tick size."""
        return (price / self.tick_size).quantize(Decimal('1')) * self.tick_size
    
    def find_high_volume_nodes(self, volume_nodes: Dict[Decimal, VolumeNode], 
                              threshold_percentile: float = 80.0) -> List[HighVolumeNode]:
        """
        Find High Volume Nodes (HVNs) - significant volume concentrations.
        
        Args:
            volume_nodes: Dictionary of volume nodes
            threshold_percentile: Percentile threshold for HVN identification
            
        Returns:
            List of HighVolumeNode objects
        """
        try:
            if not volume_nodes:
                return []
            
            # Calculate volume threshold
            volumes = [node.volume for node in volume_nodes.values()]
            threshold_volume = np.percentile(volumes, threshold_percentile)
            
            hvns = []
            for price, node in volume_nodes.items():
                if node.volume >= threshold_volume:
                    # Calculate significance (how much above average this node is)
                    avg_volume = np.mean(volumes)
                    significance = min(1.0, (node.volume - avg_volume) / avg_volume) if avg_volume > 0 else 0
                    
                    # Calculate support/resistance strength
                    # Based on volume concentration and number of times price visited
                    sr_strength = min(1.0, (node.percentage / 10.0) * (node.bar_count / 5.0))
                    
                    hvn = HighVolumeNode(
                        price=node.price,
                        volume=node.volume,
                        percentage=node.percentage,
                        bar_count=node.bar_count,
                        significance=significance,
                        support_resistance_strength=sr_strength
                    )
                    hvns.append(hvn)
            
            # Sort by volume descending
            hvns.sort(key=lambda x: x.volume, reverse=True)
            
            logger.info(f"Found {len(hvns)} High Volume Nodes")
            return hvns
            
        except Exception as e:
            logger.error(f"Error finding high volume nodes: {e}")
            return []
    
    def find_low_volume_nodes(self, volume_nodes: Dict[Decimal, VolumeNode],
                             threshold_percentile: float = 20.0) -> List[LowVolumeNode]:
        """
        Find Low Volume Nodes (LVNs) - areas of low trading activity.
        
        Args:
            volume_nodes: Dictionary of volume nodes
            threshold_percentile: Percentile threshold for LVN identification
            
        Returns:
            List of LowVolumeNode objects
        """
        try:
            if not volume_nodes:
                return []
            
            # Calculate volume threshold
            volumes = [node.volume for node in volume_nodes.values()]
            threshold_volume = np.percentile(volumes, threshold_percentile)
            
            # Find consecutive low volume areas
            sorted_prices = sorted(volume_nodes.keys())
            lvns = []
            
            i = 0
            while i < len(sorted_prices):
                price = sorted_prices[i]
                node = volume_nodes[price]
                
                if node.volume <= threshold_volume:
                    # Start of a low volume zone
                    zone_start = i
                    zone_volume = node.volume
                    
                    # Extend the zone
                    j = i + 1
                    while (j < len(sorted_prices) and 
                           volume_nodes[sorted_prices[j]].volume <= threshold_volume):
                        zone_volume += volume_nodes[sorted_prices[j]].volume
                        j += 1
                    
                    zone_end = j - 1
                    
                    if zone_end > zone_start:  # Multi-level LVN
                        # Calculate gap size
                        gap_start_price = sorted_prices[zone_start]
                        gap_end_price = sorted_prices[zone_end]
                        gap_size = float(gap_end_price - gap_start_price)
                        
                        # Calculate breakout potential
                        avg_volume = np.mean(volumes)
                        volume_deficit = max(0, avg_volume - (zone_volume / (zone_end - zone_start + 1)))
                        breakout_potential = min(1.0, volume_deficit / avg_volume) if avg_volume > 0 else 0
                        
                        # Create LVN for the gap center
                        gap_center_price = (gap_start_price + gap_end_price) / 2
                        gap_center_price = self._round_to_tick(gap_center_price)
                        
                        lvn = LowVolumeNode(
                            price=gap_center_price,
                            volume=zone_volume // (zone_end - zone_start + 1),
                            percentage=zone_volume / self.total_volume * 100 if self.total_volume > 0 else 0,
                            bar_count=sum(volume_nodes[sorted_prices[k]].bar_count 
                                        for k in range(zone_start, zone_end + 1)),
                            gap_size=gap_size,
                            breakout_potential=breakout_potential
                        )
                        lvns.append(lvn)
                    
                    i = j  # Skip to end of zone
                else:
                    i += 1
            
            logger.info(f"Found {len(lvns)} Low Volume Nodes")
            return lvns
            
        except Exception as e:
            logger.error(f"Error finding low volume nodes: {e}")
            return []
    
    def get_volume_at_price(self, price: Decimal) -> int:
        """Get volume traded at specific price level."""
        rounded_price = self._round_to_tick(price)
        return self.volume_profile.get(rounded_price, 0)
    
    def get_profile_stats(self) -> Dict[str, any]:
        """Get volume profile statistics."""
        if not self.volume_profile:
            return {}
        
        volumes = list(self.volume_profile.values())
        prices = list(self.volume_profile.keys())
        
        return {
            'total_volume': self.total_volume,
            'price_levels': len(self.volume_profile),
            'price_range': {
                'low': float(min(prices)),
                'high': float(max(prices)),
                'range': float(max(prices) - min(prices))
            },
            'volume_stats': {
                'mean': np.mean(volumes),
                'median': np.median(volumes),
                'std': np.std(volumes),
                'max': max(volumes),
                'min': min(volumes)
            }
        }


class VolumeProfileEngine:
    """High-level engine for volume profile analysis."""
    
    def __init__(self, tick_size: Decimal = Decimal('0.25')):
        """Initialize volume profile engine."""
        self.tick_size = tick_size
        self.profiles: Dict[str, VolumeProfile] = {}  # session_id -> VolumeProfile
        
    def analyze_session(self, session_id: str, data: pd.DataFrame) -> Dict[str, any]:
        """
        Analyze volume profile for a trading session.
        
        Args:
            session_id: Unique identifier for the session
            data: Session market data
            
        Returns:
            Complete session analysis
        """
        try:
            # Create volume profile
            profile = VolumeProfile(self.tick_size)
            volume_nodes = profile.build_profile(data)
            
            if not volume_nodes:
                logger.warning(f"No volume profile generated for session {session_id}")
                return {}
            
            # Store profile
            self.profiles[session_id] = profile
            
            # Find POC
            poc = POCAnalyzer.find_poc(profile.volume_profile)
            poc_zone = POCAnalyzer.find_poc_zone(profile.volume_profile)
            
            # Find HVNs and LVNs
            hvns = profile.find_high_volume_nodes(volume_nodes)
            lvns = profile.find_low_volume_nodes(volume_nodes)
            
            # Get profile statistics
            stats = profile.get_profile_stats()
            
            analysis = {
                'session_id': session_id,
                'poc': {
                    'price': float(poc) if poc else None,
                    'volume': profile.get_volume_at_price(poc) if poc else 0,
                    'zone_low': float(poc_zone[0]) if poc_zone[0] else None,
                    'zone_high': float(poc_zone[1]) if poc_zone[1] else None
                },
                'high_volume_nodes': [
                    {
                        'price': float(hvn.price),
                        'volume': hvn.volume,
                        'percentage': hvn.percentage,
                        'significance': hvn.significance,
                        'sr_strength': hvn.support_resistance_strength,
                        'is_strong_sr': hvn.is_strong_support_resistance()
                    } for hvn in hvns[:10]  # Top 10 HVNs
                ],
                'low_volume_nodes': [
                    {
                        'price': float(lvn.price),
                        'gap_size': lvn.gap_size,
                        'breakout_potential': lvn.breakout_potential,
                        'is_breakout_zone': lvn.is_potential_breakout_zone()
                    } for lvn in lvns[:5]  # Top 5 LVNs
                ],
                'statistics': stats
            }
            
            logger.info(f"Completed volume profile analysis for {session_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing session {session_id}: {e}")
            return {}
    
    def find_confluence_with_levels(self, session_id: str, pdh_pdl_levels: Dict[str, Decimal],
                                   confluence_tolerance: Decimal = Decimal('2.0')) -> List[Dict]:
        """
        Find confluence between volume profile and PDH/PDL levels.
        
        Args:
            session_id: Session identifier
            pdh_pdl_levels: Dictionary with 'pdh', 'pdl', 'midpoint' keys
            confluence_tolerance: Price tolerance for confluence detection
            
        Returns:
            List of confluence points
        """
        try:
            if session_id not in self.profiles:
                logger.warning(f"No profile found for session {session_id}")
                return []
            
            profile = self.profiles[session_id]
            volume_nodes = profile.build_profile(pd.DataFrame())  # Will use cached profile
            
            if not volume_nodes:
                return []
            
            # Find HVNs for confluence analysis
            hvns = profile.find_high_volume_nodes(volume_nodes)
            
            confluences = []
            
            # Check each PDH/PDL level for confluence with HVNs
            for level_name, level_price in pdh_pdl_levels.items():
                if level_price is None:
                    continue
                
                for hvn in hvns:
                    distance = abs(hvn.price - level_price)
                    
                    if distance <= confluence_tolerance:
                        confluence = {
                            'type': 'volume_pdh_pdl_confluence',
                            'level_name': level_name,
                            'level_price': float(level_price),
                            'hvn_price': float(hvn.price),
                            'distance': float(distance),
                            'hvn_volume': hvn.volume,
                            'hvn_significance': hvn.significance,
                            'sr_strength': hvn.support_resistance_strength,
                            'confluence_strength': min(1.0, hvn.significance + 
                                                     (1.0 - float(distance) / float(confluence_tolerance)))
                        }
                        confluences.append(confluence)
            
            # Sort by confluence strength
            confluences.sort(key=lambda x: x['confluence_strength'], reverse=True)
            
            logger.info(f"Found {len(confluences)} confluence points for {session_id}")
            return confluences
            
        except Exception as e:
            logger.error(f"Error finding confluence: {e}")
            return []
    
    def get_support_resistance_levels(self, session_id: str, 
                                    min_strength: float = 0.5) -> List[Dict]:
        """
        Get potential support/resistance levels from volume profile.
        
        Args:
            session_id: Session identifier
            min_strength: Minimum strength threshold for S/R levels
            
        Returns:
            List of support/resistance levels
        """
        try:
            if session_id not in self.profiles:
                return []
            
            profile = self.profiles[session_id]
            volume_nodes = profile.build_profile(pd.DataFrame())  # Use cached
            
            if not volume_nodes:
                return []
            
            hvns = profile.find_high_volume_nodes(volume_nodes)
            
            sr_levels = []
            for hvn in hvns:
                if hvn.support_resistance_strength >= min_strength:
                    sr_levels.append({
                        'price': float(hvn.price),
                        'strength': hvn.support_resistance_strength,
                        'volume': hvn.volume,
                        'significance': hvn.significance,
                        'type': 'volume_sr'
                    })
            
            # Sort by strength
            sr_levels.sort(key=lambda x: x['strength'], reverse=True)
            
            return sr_levels
            
        except Exception as e:
            logger.error(f"Error getting S/R levels: {e}")
            return []
    
    def clear_session(self, session_id: str):
        """Clear profile data for a session."""
        if session_id in self.profiles:
            del self.profiles[session_id]
            logger.info(f"Cleared profile data for session {session_id}")
    
    def get_session_summary(self, session_id: str) -> Dict[str, any]:
        """Get summary for a specific session."""
        if session_id not in self.profiles:
            return {}
        
        profile = self.profiles[session_id]
        poc = POCAnalyzer.find_poc(profile.volume_profile)
        
        return {
            'session_id': session_id,
            'total_volume': profile.total_volume,
            'price_levels': len(profile.volume_profile),
            'poc_price': float(poc) if poc else None,
            'price_range': profile.price_range
        }