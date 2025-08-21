# Complete Guide to Finding HVN, LVN, and POC for Market Auction Theory

## Understanding the Core Concepts

### Point of Control (POC)
The **Point of Control** is the price level with the highest traded volume during a specific period. It represents the "fairest" price where buyers and sellers agreed most, making it a powerful magnet for future price action.

### High Volume Nodes (HVN)
**High Volume Nodes** are price levels where significant trading occurred, creating areas of acceptance. These act as support/resistance because many traders have positions at these levels and will defend them.

### Low Volume Nodes (LVN)
**Low Volume Nodes** are price areas with minimal trading activity, indicating rejection. Price typically moves quickly through these zones as there's little business interest, making them excellent breakout/breakdown targets.

## Step-by-Step Calculation Process

### 1. Data Collection and Preparation

```javascript
class VolumeProfileCalculator {
  constructor(tickSize, timeframe = '30min') {
    this.tickSize = tickSize; // Price increment (0.25 for MES, 0.10 for MGC, etc.)
    this.timeframe = timeframe;
    this.volumeByPrice = new Map();
    this.priceArray = [];
    this.timestamps = [];
  }

  // Aggregate volume at each price level
  collectData(trades) {
    trades.forEach(trade => {
      // Round price to nearest tick
      const roundedPrice = Math.round(trade.price / this.tickSize) * this.tickSize;
      
      // Accumulate volume at this price
      const currentVolume = this.volumeByPrice.get(roundedPrice) || 0;
      this.volumeByPrice.set(roundedPrice, currentVolume + trade.volume);
      
      // Track for time-based analysis
      this.timestamps.push(trade.timestamp);
    });
    
    // Convert to sorted array for analysis
    this.priceArray = Array.from(this.volumeByPrice.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([price, volume]) => ({ price, volume }));
  }
}
```

### 2. Finding the Point of Control (POC)

```javascript
findPOC() {
  if (this.priceArray.length === 0) return null;
  
  // Method 1: Simple highest volume
  const poc = this.priceArray.reduce((max, current) => 
    current.volume > max.volume ? current : max
  );
  
  // Method 2: Volume-weighted POC (more accurate for wide ranges)
  const totalVolume = this.priceArray.reduce((sum, level) => sum + level.volume, 0);
  let cumulativeVolume = 0;
  let pocLevel = null;
  
  for (const level of this.priceArray) {
    cumulativeVolume += level.volume;
    if (cumulativeVolume >= totalVolume / 2) {
      pocLevel = level;
      break;
    }
  }
  
  return {
    price: poc.price,
    volume: poc.volume,
    percentOfTotal: ((poc.volume / totalVolume) * 100).toFixed(2),
    strength: this.calculatePOCStrength(poc)
  };
}

calculatePOCStrength(poc) {
  const avgVolume = this.priceArray.reduce((sum, l) => sum + l.volume, 0) / this.priceArray.length;
  const ratio = poc.volume / avgVolume;
  
  if (ratio > 3) return 'VERY_STRONG';
  if (ratio > 2) return 'STRONG';
  if (ratio > 1.5) return 'MODERATE';
  return 'WEAK';
}
```

### 3. Identifying High Volume Nodes (HVN)

```javascript
findHVN(threshold = 0.7) {
  const totalVolume = this.priceArray.reduce((sum, level) => sum + level.volume, 0);
  const avgVolume = totalVolume / this.priceArray.length;
  const hvnThreshold = avgVolume * (1 + threshold); // 70% above average
  
  const hvnNodes = [];
  
  // Find peaks in volume distribution
  for (let i = 1; i < this.priceArray.length - 1; i++) {
    const current = this.priceArray[i];
    const prev = this.priceArray[i - 1];
    const next = this.priceArray[i + 1];
    
    // Check if this is a local peak and above threshold
    if (current.volume > hvnThreshold &&
        current.volume > prev.volume &&
        current.volume > next.volume) {
      
      // Calculate HVN cluster (continuous high volume area)
      const cluster = this.expandHVNCluster(i, hvnThreshold);
      
      hvnNodes.push({
        centerPrice: current.price,
        peakVolume: current.volume,
        clusterHigh: cluster.high,
        clusterLow: cluster.low,
        totalClusterVolume: cluster.volume,
        percentOfDayVolume: ((cluster.volume / totalVolume) * 100).toFixed(2),
        priceRange: cluster.high - cluster.low,
        significance: this.rateHVNSignificance(cluster, totalVolume)
      });
      
      // Skip processed cluster
      i = cluster.endIndex;
    }
  }
  
  return hvnNodes;
}

expandHVNCluster(peakIndex, threshold) {
  let startIdx = peakIndex;
  let endIdx = peakIndex;
  let clusterVolume = this.priceArray[peakIndex].volume;
  
  // Expand left while volume remains significant
  while (startIdx > 0 && this.priceArray[startIdx - 1].volume > threshold * 0.7) {
    startIdx--;
    clusterVolume += this.priceArray[startIdx].volume;
  }
  
  // Expand right
  while (endIdx < this.priceArray.length - 1 && 
         this.priceArray[endIdx + 1].volume > threshold * 0.7) {
    endIdx++;
    clusterVolume += this.priceArray[endIdx].volume;
  }
  
  return {
    high: this.priceArray[endIdx].price,
    low: this.priceArray[startIdx].price,
    volume: clusterVolume,
    endIndex: endIdx
  };
}

rateHVNSignificance(cluster, totalVolume) {
  const percentOfTotal = cluster.volume / totalVolume;
  const priceSpan = (cluster.high - cluster.low) / this.tickSize; // ticks
  
  if (percentOfTotal > 0.2 && priceSpan < 10) return 'MAJOR'; // Tight, high volume
  if (percentOfTotal > 0.15) return 'SIGNIFICANT';
  if (percentOfTotal > 0.1) return 'MODERATE';
  return 'MINOR';
}
```

### 4. Identifying Low Volume Nodes (LVN)

```javascript
findLVN(threshold = 0.3) {
  const avgVolume = this.priceArray.reduce((sum, l) => sum + l.volume, 0) / this.priceArray.length;
  const lvnThreshold = avgVolume * threshold; // 30% of average
  
  const lvnNodes = [];
  let inLVN = false;
  let currentLVN = null;
  
  for (let i = 0; i < this.priceArray.length; i++) {
    const level = this.priceArray[i];
    
    if (level.volume < lvnThreshold) {
      if (!inLVN) {
        // Start of new LVN zone
        inLVN = true;
        currentLVN = {
          startPrice: level.price,
          endPrice: level.price,
          minVolume: level.volume,
          totalVolume: level.volume,
          levels: 1
        };
      } else {
        // Continue LVN zone
        currentLVN.endPrice = level.price;
        currentLVN.minVolume = Math.min(currentLVN.minVolume, level.volume);
        currentLVN.totalVolume += level.volume;
        currentLVN.levels++;
      }
    } else if (inLVN) {
      // End of LVN zone
      inLVN = false;
      
      // Only record significant LVN zones (at least 3 price levels)
      if (currentLVN.levels >= 3) {
        lvnNodes.push({
          highBoundary: currentLVN.endPrice,
          lowBoundary: currentLVN.startPrice,
          centerPrice: (currentLVN.endPrice + currentLVN.startPrice) / 2,
          gapSize: currentLVN.endPrice - currentLVN.startPrice,
          avgVolume: currentLVN.totalVolume / currentLVN.levels,
          minVolume: currentLVN.minVolume,
          strength: this.rateLVNStrength(currentLVN, avgVolume),
          type: this.classifyLVNType(i, currentLVN)
        });
      }
      currentLVN = null;
    }
  }
  
  return lvnNodes;
}

rateLVNStrength(lvn, avgVolume) {
  const volumeRatio = lvn.avgVolume / avgVolume;
  const gapSizeInTicks = lvn.gapSize / this.tickSize;
  
  if (volumeRatio < 0.1 && gapSizeInTicks > 10) return 'EXTREME'; // Large void
  if (volumeRatio < 0.2 && gapSizeInTicks > 5) return 'STRONG';
  if (volumeRatio < 0.3) return 'MODERATE';
  return 'WEAK';
}

classifyLVNType(index, lvn) {
  // Check what created the LVN
  const prevHigh = index > 10 ? Math.max(...this.priceArray.slice(index - 10, index).map(l => l.volume)) : 0;
  const nextHigh = index < this.priceArray.length - 10 ? 
    Math.max(...this.priceArray.slice(index, index + 10).map(l => l.volume)) : 0;
  
  if (prevHigh > lvn.avgVolume * 3 && nextHigh > lvn.avgVolume * 3) {
    return 'SEPARATION'; // LVN between two HVN areas
  } else if (prevHigh > nextHigh * 2) {
    return 'REJECTION_UP'; // Price rejected higher prices
  } else if (nextHigh > prevHigh * 2) {
    return 'REJECTION_DOWN'; // Price rejected lower prices
  }
  return 'NEUTRAL';
}
```

## Advanced Composite Profile Analysis

### Building Multi-Timeframe Profiles

```javascript
class CompositeProfileAnalyzer {
  constructor() {
    this.profiles = {
      session: new VolumeProfileCalculator(0.25, '1day'),
      weekly: new VolumeProfileCalculator(0.25, '1week'),
      monthly: new VolumeProfileCalculator(0.25, '1month')
    };
    this.compositePOCs = [];
  }

  analyzeConvergence() {
    // Find where multiple timeframe POCs align
    const sessionPOC = this.profiles.session.findPOC();
    const weeklyPOC = this.profiles.weekly.findPOC();
    const monthlyPOC = this.profiles.monthly.findPOC();
    
    const convergenceZones = [];
    
    // Check if POCs are within 1% of each other
    if (Math.abs(sessionPOC.price - weeklyPOC.price) / weeklyPOC.price < 0.01) {
      convergenceZones.push({
        price: (sessionPOC.price + weeklyPOC.price) / 2,
        strength: 'SESSION_WEEKLY_CONFLUENCE',
        reliability: 'HIGH'
      });
    }
    
    if (Math.abs(weeklyPOC.price - monthlyPOC.price) / monthlyPOC.price < 0.01) {
      convergenceZones.push({
        price: (weeklyPOC.price + monthlyPOC.price) / 2,
        strength: 'WEEKLY_MONTHLY_CONFLUENCE',
        reliability: 'VERY_HIGH'
      });
    }
    
    return convergenceZones;
  }

  findVirginPOCs() {
    // POCs that haven't been revisited (naked POCs)
    const virginPOCs = [];
    
    this.compositePOCs.forEach((poc, index) => {
      const subsequentPrices = this.compositePOCs.slice(index + 1);
      const wasRevisited = subsequentPrices.some(future => 
        future.sessionLow <= poc.price && future.sessionHigh >= poc.price
      );
      
      if (!wasRevisited) {
        virginPOCs.push({
          price: poc.price,
          date: poc.date,
          daysAgo: Math.floor((Date.now() - poc.date) / (1000 * 60 * 60 * 24)),
          strength: poc.strength,
          magnetStrength: this.calculateMagnetStrength(poc)
        });
      }
    });
    
    return virginPOCs.sort((a, b) => b.magnetStrength - a.magnetStrength);
  }

  calculateMagnetStrength(poc) {
    // Factors: recency, volume, day type
    const recencyScore = Math.max(0, 10 - poc.daysAgo * 0.5);
    const volumeScore = poc.volume > this.avgDailyVolume * 1.5 ? 10 : 5;
    const strengthScore = poc.strength === 'VERY_STRONG' ? 10 : 5;
    
    return (recencyScore + volumeScore + strengthScore) / 3;
  }
}
```

## Trading Application Strategies

### 1. HVN Trading Rules

```javascript
class HVNTradingStrategy {
  executeHVNBounce(currentPrice, hvnLevels) {
    const nearestHVN = this.findNearestHVN(currentPrice, hvnLevels);
    
    if (!nearestHVN) return null;
    
    const distance = Math.abs(currentPrice - nearestHVN.centerPrice);
    const approach = distance / this.atr; // Distance in ATR units
    
    // Entry conditions
    if (approach < 0.5) { // Within 0.5 ATR of HVN
      const signal = {
        type: currentPrice < nearestHVN.centerPrice ? 'LONG' : 'SHORT',
        entry: nearestHVN.centerPrice,
        stop: currentPrice < nearestHVN.centerPrice ? 
          nearestHVN.clusterLow - this.atr * 0.5 : 
          nearestHVN.clusterHigh + this.atr * 0.5,
        target1: this.poc.price, // First target at POC
        target2: null, // Set based on next HVN/LVN
        confidence: this.calculateHVNConfidence(nearestHVN),
        expectedHoldTime: '15-30 minutes'
      };
      
      // Find target 2 based on profile structure
      const nextLevel = this.findNextSignificantLevel(currentPrice, signal.type);
      signal.target2 = nextLevel.price;
      
      return signal;
    }
    
    return null;
  }

  calculateHVNConfidence(hvn) {
    let score = 50; // Base confidence
    
    // Adjustments
    if (hvn.significance === 'MAJOR') score += 20;
    if (hvn.percentOfDayVolume > 15) score += 10;
    if (hvn.priceRange < this.atr) score += 10; // Tight HVN
    if (this.timeInSession < 60) score -= 10; // Early session, less reliable
    
    return Math.min(90, Math.max(10, score));
  }
}
```

### 2. LVN Breakout Strategy

```javascript
class LVNBreakoutStrategy {
  executeLVNBreakout(currentPrice, lvnLevels, momentum) {
    const nearestLVN = this.findNearestLVN(currentPrice, lvnLevels);
    
    if (!nearestLVN) return null;
    
    // Check if price is approaching LVN
    const distanceToLVN = Math.min(
      Math.abs(currentPrice - nearestLVN.highBoundary),
      Math.abs(currentPrice - nearestLVN.lowBoundary)
    );
    
    if (distanceToLVN < this.atr * 0.3) { // Very close to LVN
      const direction = currentPrice < nearestLVN.centerPrice ? 'SHORT' : 'LONG';
      
      // Momentum confirmation
      if ((direction === 'LONG' && momentum > 0) || 
          (direction === 'SHORT' && momentum < 0)) {
        
        return {
          type: direction,
          entry: direction === 'LONG' ? nearestLVN.highBoundary : nearestLVN.lowBoundary,
          stop: direction === 'LONG' ? nearestLVN.lowBoundary : nearestLVN.highBoundary,
          target: this.findNextHVN(nearestLVN.centerPrice, direction),
          confidence: this.calculateLVNBreakoutProbability(nearestLVN, momentum),
          notes: `LVN gap: ${nearestLVN.gapSize.toFixed(2)}, Strength: ${nearestLVN.strength}`
        };
      }
    }
    
    return null;
  }

  calculateLVNBreakoutProbability(lvn, momentum) {
    let probability = 50;
    
    // LVN characteristics
    if (lvn.strength === 'EXTREME') probability += 20;
    if (lvn.type === 'SEPARATION') probability += 15; // Clean separation
    if (lvn.gapSize > this.atr * 2) probability += 10; // Large gap
    
    // Momentum confirmation
    if (Math.abs(momentum) > 0.7) probability += 15;
    
    // Time of day (breakouts work better in first 2 hours)
    if (this.minutesIntoSession < 120) probability += 10;
    
    return Math.min(85, probability);
  }
}
```

### 3. POC Magnet Trade

```javascript
class POCMagnetStrategy {
  executePOCReversion(currentPrice, poc, marketContext) {
    const distanceToPOC = Math.abs(currentPrice - poc.price);
    const distanceInATR = distanceToPOC / this.atr;
    
    // POC magnet effect is strongest when price is extended
    if (distanceInATR > 2 && distanceInATR < 4) {
      const signal = {
        type: currentPrice > poc.price ? 'SHORT' : 'LONG',
        entry: currentPrice,
        stop: currentPrice + (currentPrice > poc.price ? this.atr : -this.atr),
        target1: poc.price,
        target2: poc.price + (currentPrice > poc.price ? -this.atr * 0.5 : this.atr * 0.5),
        confidence: this.calculatePOCMagnetStrength(poc, distanceInATR, marketContext),
        timeframe: '30-60 minutes expected'
      };
      
      // Risk management
      signal.positionSize = signal.confidence > 70 ? 1.0 : 0.5; // Full or half size
      signal.maxHoldTime = 90; // minutes
      
      return signal;
    }
    
    return null;
  }

  calculatePOCMagnetStrength(poc, distance, context) {
    let strength = 40; // Base strength
    
    // POC characteristics
    if (poc.strength === 'VERY_STRONG') strength += 20;
    if (poc.percentOfTotal > 10) strength += 10;
    
    // Distance factor (sweet spot is 2-3 ATR)
    if (distance > 2 && distance < 3) strength += 15;
    
    // Market context
    if (context.dayType === 'NORMAL_DAY') strength += 10; // POC magnets work best in balanced markets
    if (context.trendStrength < 30) strength += 10; // Low trend = higher reversion probability
    
    // Time decay (POC weakens late in session)
    const minutesLeft = 390 - this.minutesIntoSession; // 6.5 hour session
    if (minutesLeft < 60) strength -= 20;
    
    return Math.max(20, Math.min(90, strength));
  }
}
```

## Real-Time Implementation Tips

### Visual Identification on Charts

1. **Color Coding System**:
   - POC: Bright yellow/gold line (thickest)
   - HVN: Blue zones with opacity based on volume
   - LVN: Red/pink zones or dotted lines
   - Virgin POCs: Purple diamonds

2. **Minimum Requirements**:
   - At least 1000 ticks of data per session
   - Update calculations every 5-10 seconds
   - Store last 20 sessions for naked POC tracking

3. **Performance Optimization**:
   ```javascript
   // Use incremental updates instead of full recalculation
   updateVolumeProfile(newTrade) {
     const roundedPrice = Math.round(newTrade.price / this.tickSize) * this.tickSize;
     const currentVol = this.volumeByPrice.get(roundedPrice) || 0;
     this.volumeByPrice.set(roundedPrice, currentVol + newTrade.volume);
     
     // Only recalculate POC if this price's volume exceeds current POC
     if (currentVol + newTrade.volume > this.currentPOC.volume) {
       this.currentPOC = { price: roundedPrice, volume: currentVol + newTrade.volume };
     }
   }
   ```

### Common Pitfalls to Avoid

1. **Over-reliance on single timeframe**: Always check multiple timeframes for confluence
2. **Ignoring market context**: POCs work differently in trending vs. balanced markets
3. **Not accounting for session breaks**: Overnight POCs have different characteristics
4. **Fixed parameters**: Adapt HVN/LVN thresholds based on market volatility
5. **Late session POCs**: Their magnetic effect diminishes in the last hour

## Integration with TopStepX Bot

```javascript
class TopStepVolumeProfileBot {
  constructor(symbol) {
    this.symbol = symbol;
    this.profile = new VolumeProfileCalculator(this.getTickSize(symbol));
    this.analyzer = new CompositeProfileAnalyzer();
    this.strategies = {
      hvnBounce: new HVNTradingStrategy(),
      lvnBreakout: new LVNBreakoutStrategy(),
      pocMagnet: new POCMagnetStrategy()
    };
  }

  async analyzeAndTrade(marketData) {
    // Update profile with latest data
    this.profile.collectData(marketData.trades);
    
    // Calculate key levels
    const poc = this.profile.findPOC();
    const hvnLevels = this.profile.findHVN();
    const lvnLevels = this.profile.findLVN();
    
    // Check each strategy
    const signals = [];
    
    signals.push(this.strategies.hvnBounce.executeHVNBounce(marketData.currentPrice, hvnLevels));
    signals.push(this.strategies.lvnBreakout.executeLVNBreakout(marketData.currentPrice, lvnLevels, marketData.momentum));
    signals.push(this.strategies.pocMagnet.executePOCReversion(marketData.currentPrice, poc, marketData.context));
    
    // Filter and rank signals
    const validSignals = signals.filter(s => s && s.confidence > 60);
    validSignals.sort((a, b) => b.confidence - a.confidence);
    
    // Execute highest confidence signal
    if (validSignals.length > 0) {
      await this.executeTrade(validSignals[0]);
    }
  }

  getTickSize(symbol) {
    const sizes = {
      'MES': 0.25,
      'MGC': 0.10,
      'MCL': 0.01,
      'SIL': 0.005,
      'MNG': 0.25
    };
    return sizes[symbol];
  }
}
```

## Key Takeaways

1. **POC** = Highest volume price = Market consensus fair value
2. **HVN** = High volume areas = Support/Resistance zones
3. **LVN** = Low volume gaps = Acceleration zones
4. **Virgin POCs** = Unvisited POCs = Future price magnets
5. **Composite profiles** = Multiple timeframe confluence = Highest probability levels

Success comes from combining these levels with market context, time of day, and momentum confirmation. Never trade levels in isolation - always confirm with at least two other factors before entering a position.