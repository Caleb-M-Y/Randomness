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
// bring in the classes
#include "area.h"
#include "volume.h"

using namespace std;

// ####################################################################################################################################################################################
// GLOBAL VARIABLES 

// variable for area and volume selections
string sel1;
string sel2;
string sel3;


// ####################################################################################################################################################################################
// MAIN FUNCTION

int main()
{
	cout << "This program allows you to select select a type of area or volume to calculate then does it for you." << endl;
	cout << "Please type 'volume' or 'area', or 'v' or 'a' below to select: " << endl;
	cin >> sel1;

	// AREA
	if (sel1 == "area" || sel1 == "a" || sel1 == "Area")
	{
		cout << "What shape's area would you like to calculate? " << endl;
		cout << "Your options are rectangle, circle, and triangle. " << endl;
		cin >> sel2;

		if (sel2 == "rectangle" || sel2 == "r" || sel2 == "Rectangle")
		{
			// 1. create specific object
			Rectangle rec;

			// 2. ask the user for the variables
			rec.askforVariables();

			// 3. calculate and print
			cout << "The area is: " << rec.calculateArea() << endl << endl;

		}
		else if (sel2 == "circle" || sel2 == "c" || sel2 == "Circle")
		{
			// 1. create specific object
			Circle circle;

			// 2. ask the user for the variables
			circle.askforVariables();

			// 3. calculate and print
			cout << "The area is: " << circle.calculateArea() << endl << endl;

		}
		else if (sel2 == "triangle" || sel2 == "t" || sel2 == "Triangle")
		{
			// 1. create specific object
			Triangle tri;

			// 2. ask the user for the variables
			tri.askforVariables();

			// 3. calculate and print
			cout << "The area is: " << tri.calculateArea() << endl << endl;

		}
	}

	// VOLUME
	else if (sel1 == "volume" || sel1 == "v" || sel1 == "Volume")
	{
		cout << "Options for volume calculations are cuboid, sphere, hemisphere, cylinder, cone, pyramid, and prism. " << endl;
		cout << "Type in one of these options to select: ";
		cin >> sel2;
		cout << endl;
		if (sel2 == "cuboid" || sel2 == "cube" || sel2 == "Cuboid" || sel2 == "Cube")
		{
			// 1. create specific object
			Cube cube;

			// 2. ask the user for the variables
			cube.askforVariables();

			// 3. calculate and print
			cout << "The volume is: " << cube.calculateVolume() << endl << endl;

		}
		else if (sel2 == "sphere" || sel2 == "Sphere")
		{
			// 1. create specific object
			Sphere sph;

			// 2. ask the user for the variables
			sph.askforVariables();

			// 3. calculate and print
			cout << "The volume is: " << sph.calculateVolume() << endl << endl;

		}
		else if (sel2 == "hemisphere" || sel2 == "Hemisphere")
		{
			// 1. create specific object
			Hemisphere hem;

			// 2. ask the user for the variables
			hem.askforVariables();

			// 3. calculate and print
			cout << "The volume is: " << hem.calculateVolume() << endl << endl;

		}
		else if (sel2 == "cylinder" || sel2 == "Cylinder" || sel2 == "cyl")
		{
			// 1. create specific object
			Cylinder cyl;

			// 2. ask the user for the variables
			cyl.askforVariables();

			// 3. calculate and print
			cout << "The volume is: " << cyl.calculateVolume() << endl << endl;

		}
		else if (sel2 == "cone" || sel2 == "Cone" || sel2 == "c")
		{
			// 1. create specific object
			Cone cone;

			// 2. ask the user for the variables
			cone.askforVariables();

			// 3. calculate and print
			cout << "The volume is: " << cone.calculateVolume() << endl << endl;

		}
	}

}

// ####################################################################################################################################################################################
