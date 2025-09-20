/**
 * @file Debug.h
 * @brief Debug 工具, 抄自 Torist
 * @author Cao Xin
 * @date 2025-09-20
 */

#pragma once
#include <Arduino.h>
#include <iterator>
#include <string>
#include <utility>
#include <vector>
#include <set>
#include <map>

// --- to_string for built-ins ---
inline String to_string(const String &s) { return "\"" + s + "\""; }
inline String to_string(const char *s) { return "\"" + String(s) + "\""; }
inline String to_string(char c) { return "'" + String(c) + "'"; }
inline String to_string(bool x) { return x ? "true" : "false"; }
inline String to_string(int x) { return String(x); }
inline String to_string(long x) { return String(x); }
inline String to_string(unsigned int x) { return String(x); }
inline String to_string(unsigned long x) { return String(x); }
inline String to_string(float x) { return String(x); }
inline String to_string(double x) { return String(x); }

// --- to_string for pair ---
template<class A, class B>
String to_string(const std::pair<A, B> &p) {
    return "(" + to_string(p.first) + ", " + to_string(p.second) + ")";
}

// --- to_string for containers ---
template<class C>
auto to_string(const C &v) -> decltype(std::begin(v), std::end(v), String()) {
    String res = "{";
    bool first = true;
    for (auto it = std::begin(v); it != std::end(v); ++it) {
        if (!first) res += ", ";
        first = false;
        res += to_string(*it);
    }
    res += "}";
    return res;
}

// --- debug_out declarations ---
inline void debug_out() { Serial.println(); }

template<class H, class... T>
void debug_out(const H &h, const T &... t) {
    Serial.print(" ");
    Serial.print(to_string(h));
    debug_out(t...);
}

// --- debug macro ---
#define debug(...) \
    Serial.print("["); Serial.print(#__VA_ARGS__); Serial.print("]:"); debug_out(__VA_ARGS__)
