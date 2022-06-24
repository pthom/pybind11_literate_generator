#pragma once


// <litgen_boxed_types_header> // Autogenerated code below! Do not edit!
// <Autogenerated_Boxed_Types>
struct BoxedBool
{
    bool value;
    BoxedBool(bool v = false) : value(v) {}
    std::string __repr__() const { return std::string("BoxedBool(") + std::to_string(value) + ")"; }
};
struct BoxedInt
{
    int value;
    BoxedInt(int v = 0) : value(v) {}
    std::string __repr__() const { return std::string("BoxedInt(") + std::to_string(value) + ")"; }
};
struct BoxedUnsignedInt
{
    unsigned int value;
    BoxedUnsignedInt(unsigned int v = 0) : value(v) {}
    std::string __repr__() const { return std::string("BoxedUnsignedInt(") + std::to_string(value) + ")"; }
};
struct BoxedFloat
{
    float value;
    BoxedFloat(float v = 0.) : value(v) {}
    std::string __repr__() const { return std::string("BoxedFloat(") + std::to_string(value) + ")"; }
};
struct BoxedString
{
    std::string value;
    BoxedString(std::string v = "") : value(v) {}
    std::string __repr__() const { return std::string("BoxedString(") + value + ")"; }
};
struct BoxedDouble
{
    double value;
    BoxedDouble(double v = 0.) : value(v) {}
    std::string __repr__() const { return std::string("BoxedDouble(") + std::to_string(value) + ")"; }
};
// </Autogenerated_Boxed_Types>

// </litgen_boxed_types_header>