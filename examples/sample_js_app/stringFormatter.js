/**
 * String formatter module - String manipulation functions
 * @module stringFormatter
 */

/**
 * Convert string to camelCase
 */
function toCamelCase(str) {
    return str
        .toLowerCase()
        .replace(/[^a-zA-Z0-9]+(.)/g, (_, chr) => chr.toUpperCase());
}

/**
 * Convert string to snake_case
 */
function toSnakeCase(str) {
    return str
        .replace(/([A-Z])/g, '_$1')
        .toLowerCase()
        .replace(/^_/, '');
}

/**
 * Capitalize first letter
 */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Truncate string with ellipsis
 */
function truncate(str, maxLength, suffix = '...') {
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * Count words in string
 */
function wordCount(str) {
    return str.trim().split(/\s+/).filter(word => word.length > 0).length;
}

module.exports = {
    toCamelCase,
    toSnakeCase,
    capitalize,
    truncate,
    wordCount
};
