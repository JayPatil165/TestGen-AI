/**
 * Object utilities module - Object manipulation functions
 * @module objectUtils
 */

/**
 * Deep clone an object
 */
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Merge multiple objects
 */
function merge(...objects) {
    return Object.assign({}, ...objects);
}

/**
 * Pick specific keys from object
 */
function pick(obj, keys) {
    return keys.reduce((result, key) => {
        if (key in obj) {
            result[key] = obj[key];
        }
        return result;
    }, {});
}

/**
 * Omit specific keys from object
 */
function omit(obj, keys) {
    const result = { ...obj };
    keys.forEach(key => delete result[key]);
    return result;
}

/**
 * Check if object is empty
 */
function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}

module.exports = {
    deepClone,
    merge,
    pick,
    omit,
    isEmpty
};
