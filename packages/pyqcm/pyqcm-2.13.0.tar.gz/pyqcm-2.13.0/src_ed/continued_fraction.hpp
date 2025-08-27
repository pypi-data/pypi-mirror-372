/*
 Class for a Jacobi continued fraction
 */

#ifndef continued_fraction_h
#define continued_fraction_h

#include <cstdio>

#include "block_matrix.hpp"

//! Represents a truncated Jacobi continued fraction.
struct continued_fraction
{

	vector<double> a; 	//!< array of partial denominators
	vector<double> b; 	//!< array partial numerators
	
  continued_fraction();
  continued_fraction(const vector<double>& _a, const vector<double>& _b);
  continued_fraction(vector<double>& _a, vector<double>& _b, double e0, double norm, bool create);
  Complex evaluate(Complex z);
};


std::ostream& operator<<(std::ostream &flux, const continued_fraction &F);
std::istream& operator>>(std::istream &flux, continued_fraction &F);



#endif
