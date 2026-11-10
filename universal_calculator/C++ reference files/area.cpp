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
#include "area.h"

using namespace std;

// ####################################################################################################################################################################################


// Constructor: Set default values when a circle is created
Circle::Circle()
{
	radius = 0.0;
}

// define functions with logic in them
void Circle::askforVariables()
{
	cout << "What is the radius of the circle? " << endl;
	cin >> radius;

	if (radius >= 0)
		radius = radius;
	else
		do
		{
			cout << "Invalid radius entry. Enter a valid radius: ";
			cin >> radius;
		} while (radius < 0);
}

double Circle::calculateArea()
{
	return M_PI * pow(radius, 2);
}

// ####################################################################################################################################################################################
// TRIANGLE IMPLEMENTATION
// ####################################################################################################################################################################################

Triangle::Triangle()
{
    // Initialize our specific triangle variables
    base = 0.0;
    height = 0.0;
    // Note: We don't need to initialize 'frac' here because you already 
    // initialized it beautifully in your area.h file!
}

void Triangle::askforVariables()
{
    cout << "What is the base width of the triangle? " << endl;
    cin >> base;

    while (base < 0)
    {
        cout << "Invalid entry. Enter a valid positive base width: ";
        cin >> base;
    }

    cout << "What is the height of the triangle? " << endl;
    cin >> height;

    while (height < 0)
    {
        cout << "Invalid entry. Enter a valid positive height: ";
        cin >> height;
    }
}

double Triangle::calculateArea()
{
    return frac * base * height;
}

// ####################################################################################################################################################################################
// RECTANGLE IMPLEMENTATION
// ####################################################################################################################################################################################

Rectangle::Rectangle()
{
    width = 0.0;
    length = 0.0;
}

void Rectangle::askforVariables()
{
    cout << "What is the width of the rectangle? " << endl;
    cin >> width;

    while (width < 0)
    {
        cout << "Invalid entry. Enter a valid positive width: ";
        cin >> width;
    }

    cout << "What is the length of the rectangle? " << endl;
    cin >> length;

    while (length < 0)
    {
        cout << "Invalid entry. Enter a valid positive length: ";
        cin >> length;
    }
}

double Rectangle::calculateArea()
{
    return width * length;
}
