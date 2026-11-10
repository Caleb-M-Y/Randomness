#pragma once

class Circle
{
private:
	// private variable
	double radius;

public:
	// constructuor (sets up a blank circle)
	Circle();

	// functions inside of class
	void askforVariables();
	double calculateArea();
};



class Triangle
{
private: 
	// variables
	double base;
	double height;
	double frac = 1.00 / 2.00;

public:
	// Constructor (sets up blank shape)
	Triangle();

	// functions inside class
	void askforVariables();
	double calculateArea();
};



class Rectangle
{
private: 
	// variables
	double width;
	double length;

public:
	// Constructor (sets up blank shape)
	Rectangle();

	// functions inside class
	void askforVariables();
	double calculateArea();
};