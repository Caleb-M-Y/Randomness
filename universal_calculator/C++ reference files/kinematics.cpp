#include "kinematics.h"
#include <iostream>

using namespace std;

VelocityEquation::VelocityEquation()
{
    v = 0.0;
    v0 = 0.0;
    a = 0.0;
    t = 0.0;
    var = "";
}

void VelocityEquation::askforVariables()
{
    cout << "Equation: v = v0 + at" << endl;
    cout << "Which variable are you trying to find? (type 'v', 'v0', 'a', or 't'): ";
    cin >> var;
    cout << endl;

    // Ask for everything EXCEPT the missing variable
    if (var != "v")
    {
        cout << "Enter final velocity (v): ";
        cin >> v;
    }
    if (var != "v0")
    {
        cout << "Enter initial velocity (v0): ";
        cin >> v0;
    }
    if (var != "a")
    {
        cout << "Enter acceleration (a): ";
        cin >> a;
    }
    if (var != "t")
    {
        cout << "Enter time (t): ";
        cin >> t;
    }
}

double VelocityEquation::calculateResult()
{
    // Run the correctly rearranged equation based on what is missing
    if (var == "v")
    {
        return v0 + (a * t);
    }
    else if (var == "v0")
    {
        return v - (a * t);
    }
    else if (var == "a")
    {
        return (v - v0) / t;
    }
    else if (var == "t")
    {
        return (v - v0) / a;
    }
    else
    {
        cout << "Error: Unknown target variable." << endl;
        return 0.0;
    }
}