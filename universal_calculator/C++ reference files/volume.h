#pragma once

class Cube
{
private:
	// private variable
	double length;
	double width;
	double height;

public:
	// constructuor (sets up a blank Cube)
	Cube();

	// functions inside of class
	void askforVariables();
	double calculateVolume();
};


class Sphere
{
private:
	double radius;
	double frac = 4.00 / 3.00;

public:
	Sphere();

	void askforVariables();
	double calculateVolume();
};


class Hemisphere
{
private:
	double radius;
	double frac = 2.00 / 3.00;

public:
	Hemisphere();

	void askforVariables();
	double calculateVolume();
};


class Cylinder
{
private:
	double radius;
	double height;

public:
	Cylinder();

	void askforVariables();
	double calculateVolume();
};


class Cone
{
private:
	double radius;
	double height;
	double frac = 1.00 / 3.00;

public:
	Cone();

	void askforVariables();
	double calculateVolume();
};