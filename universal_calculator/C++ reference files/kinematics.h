#pragma once

#include <string>
using namespace std;

// This header file is use to create classes for the kinematic equations
// The user will be able to select a variable they want to find 
// and the code will calculate it for them. 

// 1: v = v0 + at                - velocity
// 2: x = x0 + v0t + 1/2 at^2    - displacement
// 3: v^2 = v0^2 + 2a(x - x0)    - timeless
// 4: x = x0 + 1/2 (v0 + v)t     - average displacement

class VelocityEquation
{
private:
	// four variables in the equation
	double v; // final velocity
	double v0; // initial vel
	double a; // acceleration
	double t; // time duh

	// Create variable to store what the user wants to find
	string var;

public:
	VelocityEquation();

	void askforVariables();
	double calculateResult();
};