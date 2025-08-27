#pragma once

#include <vector>
#include <Arduino.h>

/**
 * @brief Split a string by a single delimiter character.
 *
 * @param str The input string to split.
 * @param ch  The delimiter character.
 * @return A vector of substrings obtained after splitting.
 */
std::vector<String> split(String str, char ch);

/**
 * @brief Clamp a value to the range [minVal, maxVal].
 *
 * @tparam T Value type (must support < and >).
 * @param value Input value.
 * @param minVal Lower bound.
 * @param maxVal Upper bound.
 * @return The clamped value.
 */
template<typename T>
inline T clip(const T& value, const T& minVal, const T& maxVal) {
    if (value < minVal) return minVal;
    if (value > maxVal) return maxVal;
    return value;
}