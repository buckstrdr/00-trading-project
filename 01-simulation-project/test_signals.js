const strategy = new (require('./strategies/test_js_strategy.js'))({shortPeriod: 3, longPeriod: 5});

// Send rising prices to trigger BUY signal
const prices = [100, 100.5, 99.8, 100.2, 101, 102, 103, 104, 105, 106];
prices.forEach((price, i) => {
    const signal = strategy.analyze({close: price});
    if (signal !== 'HOLD') {
        console.log(`Bar ${i}: Price=${price}, Signal=${signal}`);
    }
});

// Send falling prices to trigger SELL signal  
const fallingPrices = [106, 105, 104, 103, 102, 101, 100, 99, 98];
fallingPrices.forEach((price, i) => {
    const signal = strategy.analyze({close: price});
    if (signal !== 'HOLD') {
        console.log(`Bar ${i+10}: Price=${price}, Signal=${signal}`);
    }
});
