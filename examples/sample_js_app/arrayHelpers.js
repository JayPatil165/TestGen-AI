/**
 * Array helper module - Array manipulation utilities
 * @module arrayHelpers
 */

/**
 * Find unique elements in array
 */
function unique(arr) {
    return [...new Set(arr)];
}

/**
 * Flatten nested array
 */
function flatten(arr) {
    return arr.reduce((acc, val) =>
        Array.isArray(val) ? acc.concat(flatten(val)) : acc.concat(val), []
    );
}

/**
 * Chunk array into smaller arrays
 */
function chunk(arr, size) {
    const chunks = [];
    for (let i = 0; i < arr.length; i += size) {
        chunks.push(arr.slice(i, i + size));
    }
    return chunks;
}

/**
 * Find intersection of two arrays
 */
function intersection(arr1, arr2) {
    return arr1.filter(item => arr2.includes(item));
}

/**
 * Remove falsy values from array
 */
function compact(arr) {
    return arr.filter(Boolean);
}

module.exports = {
    unique,
    flatten,
    chunk,
    intersection,
    compact
};
