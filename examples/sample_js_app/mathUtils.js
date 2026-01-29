/**
 * Math utilities module - Simple mathematical operations
 * @module mathUtils
 */

/**
 * Add two numbers
 */
function add(a, b) {
    return a + b;
}

/**
 * Subtract b from a
 */
function subtract(a, b) {
    return a - b;
}

/**
 * Multiply two numbers
 */
function multiply(a, b) {
    return a * b;
}

/**
 * Divide a by b
 */
function divide(a, b) {
    if (b === 0) {
        throw new Error('Cannot divide by zero');
    }
    return a / b;
}

/**
 * Calculate factorial
 */
function factorial(n) {
    if (n < 0) throw new Error('Negative numbers not allowed');
    if (n === 0 || n === 1) return 1;
    return n * factorial(n - 1);
}

module.exports = {
    add,
    subtract,
    multiply,
    divide,
    factorial
};
