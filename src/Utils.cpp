#include "Utils.hpp"

#include <vector>
#include <Arduino.h>

/**
 * @brief split string with single char
 * @param str string to splt
 * @param ch char to split
 */
std::vector<String> split(String str, char ch) {
    std::vector<String> res;
    String temp = "";
    for (char c : str) {
        if (c == ch) {
            res.push_back(temp);
            temp = "";
            continue;
        }
        temp += c;
    }
    res.push_back(temp);
    return res;
}