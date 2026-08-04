// defines like this must be at the top
#define _USE_MATH_DEFINES

// basic iostream stuff 
#include <iostream>
// include cmath so we can use that library
#include <cmath>
// library stands for Input/Output Manipulation. It gives you tools to format how your text prints out. 
// For example, if you wanted to print the area of your circle to exactly two decimal places, you would use setprecision(2) from the <iomanip> library!
#include <iomanip>
// strings obviously
#include <string>
// include the area class
#include "volume.h"

using namespace std;

// ####################################################################################################################################################################################

// ####################################################################################################################################################################################
// Cube IMPLEMENTATION
// ####################################################################################################################################################################################

Cube::Cube()
{
	length = 0.0;
	width = 0.0;
	height = 0.0;
}

void Cube::askforVariables()
{
	// WIDTH
	cout << "whats the width: ";
	cin >> width;

	if (width >= 0)
		width = width;
	else
		do
		{
			cout << "Invalid width entry. Enter a valid width: ";
			cin >> width;
		} while (width < 0);


	cout << endl;

	// LENGTH
	cout << "whats the length: ";
	cin >> length;

	if (length >= 0)
		length = length;
	else
		do
		{
			cout << "Invalid width entry. Enter a valid length: ";
			cin >> length;
		} while (length < 0);

	// HEIGHT
	cout << "whats the height: ";
	cin >> height;

	if (height >= 0)
		height = height;
	else
		do
		{
			cout << "Invalid width entry. Enter a valid height: ";
			cin >> height;
		} while (height < 0);
}

double Cube::calculateVolume()
{
	return length * width * height;
}

// ####################################################################################################################################################################################
// SPHERE IMPLEMENTATION
// ####################################################################################################################################################################################

Sphere::Sphere()
{
	radius = 0.0;
}

void Sphere::askforVariables()
{
	// formula is V = (4/3) * pi * r^3

	cout << "formula is V = (4/3) * pi * r^3" << endl;
	cout << "What is the radius of the sphere? " << endl;
	cin >> radius;

	while (radius < 0)
	{
		cout << "Invalid radius entry. Enter a valid radius: ";
		cin >> radius;
	}
}

double Sphere::calculateVolume()
{
	return frac * M_PI * pow(radius, 3);
}

// ####################################################################################################################################################################################
// HEMISPHERE IMPLEMENTATION
// ####################################################################################################################################################################################

Hemisphere::Hemisphere()
{
	radius = 0.0;
}

void Hemisphere::askforVariables()
{
	// formula is V = (2/3) * pi * r^3

	cout << "formula is V = (2/3) * pi * r^3" << endl;
	cout << "What is the radius of the hemisphere? " << endl;
	cin >> radius;

	while (radius < 0)
	{
		cout << "Invalid radius entry. Enter a valid radius: ";
		cin >> radius;
	}
}

double Hemisphere::calculateVolume()
{
	return frac * M_PI * pow(radius, 3);
}

// ####################################################################################################################################################################################
// CYLINDER IMPLEMENTATION
// ####################################################################################################################################################################################

Cylinder::Cylinder()
{
	radius = 0.0;
	height = 0.0;
}

void Cylinder::askforVariables()
{
	// formula is V = pi * r^2 * h

	cout << "formula is V = pi * r^2 * h" << endl;
	cout << "What is the radius of the cylinder? " << endl;
	cin >> radius;

	while (radius < 0)
	{
		cout << "Invalid radius entry. Enter a valid radius: ";
		cin >> radius;
	}

	cout << "What is the height of the cylinder? " << endl;
	cin >> height;

	while (height < 0)
	{
		cout << "Invalid height entry. Enter a valid height: ";
		cin >> height;
	}
}

double Cylinder::calculateVolume()
{
	return M_PI * pow(radius, 2) * height;
}

// ####################################################################################################################################################################################
// CONE IMPLEMENTATION
// ####################################################################################################################################################################################

Cone::Cone()
{
	radius = 0.0;
	height = 0.0;
}

void Cone::askforVariables()
{
	cout << "formula is V = 1/3 * pi * r^2 * h" << endl;
	cout << "What is the radius of the cone? " << endl;
	cin >> radius;

	while (radius < 0)
	{
		cout << "Invalid radius entry. Enter a valid radius: ";
		cin >> radius;
	}

	cout << "What is the height of the cone? " << endl;
	cin >> height;

	while (height < 0)
	{
		cout << "Invalid height entry. Enter a valid height: ";
		cin >> height;
	}
}

double Cone::calculateVolume()
{
	return frac * M_PI * pow(radius, 2) * height;
}