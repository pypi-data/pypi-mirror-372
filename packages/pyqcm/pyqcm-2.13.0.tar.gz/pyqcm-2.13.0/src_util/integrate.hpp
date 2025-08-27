#ifndef integrate_h
#define integrate_h

#include <cmath>
#include <vector>
#include "parser.hpp"
#include "vector_num.hpp"

#define MAX_GAUSS_KRONROD_RECURSION 10 //! maximum recursion level in gauss_kronrod
#define MIN_GAUSS_KRONROD_RECURSION 2  //! minimum recursion level in gauss_kronrod

extern double GK_x[8];
extern double GK_w[8];
extern double GK_gw[4];

extern int integrator_ncomp;

//! in-house integrator of functions of one variable
/**
one-dimensional integrator template
assumes that T is a structure, with the following interface:
T f
f.ncomp = number of components
f(x, v) where x = double (argument) and v = vector<double> = values
 */
template <typename T>
struct Integrator_GK_region{
	
	double a; // start
	double b; // end
	vector<double> value; // value of the integrals in the region
	double err; // value of the largest quadratic error among the components
	
	Integrator_GK_region(double _a, double _b, T integrand) : a(_a), b(_b), err(0.0)
	{
		int ncomp = (int)integrand.ncomp;
		value.resize(ncomp);
		
		double alpha = 0.5*(b-a);
		double beta = 0.5*(b+a);
		
		// filling the array of abcissas
		vector<double> x(15);
		x[0] = alpha*GK_x[0] + beta;
		for(int j=1; j<4; ++j){
			x[j] =  alpha*GK_x[j] + beta;
			x[j+3] = -alpha*GK_x[j] + beta;
		}
		for(int j=4; j<8; ++j){
			x[j+3] =  alpha*GK_x[j] + beta;
			x[j+7] = -alpha*GK_x[j] + beta;
		}
		
		
		// allocating space for the values
		vector<vector<double> > v(15);
		v.assign(15, vector<double>(ncomp));
		
		for(int j=0; j<15; j++) integrand(x[j],v[j]);
		
		vector<double> integral_G(ncomp);
		vector<double>& integral_K = value;
		integral_G.resize(ncomp);
		
		for(int i=0; i<ncomp; ++i) integral_G[i] += GK_gw[0]*v[0][i];
		for(int i=0; i<ncomp; ++i) integral_K[i] +=  GK_w[0]*v[0][i];
		int k;
		for(int j=1; j<4; ++j){
			k = j;
			for(int i=0; i<ncomp; ++i) integral_G[i] += GK_gw[j]*v[k][i];
			for(int i=0; i<ncomp; ++i) integral_K[i] +=  GK_w[j]*v[k][i];
			k = j+3;
			for(int i=0; i<ncomp; ++i) integral_G[i] += GK_gw[j]*v[k][i];
			for(int i=0; i<ncomp; ++i) integral_K[i] +=  GK_w[j]*v[k][i];
		}
		for(int j=4; j<8; ++j){
			k = j+3;
			for(int i=0; i<ncomp; ++i) integral_K[i] +=  GK_w[j]*v[k][i];
			k = j+7;
			for(int i=0; i<ncomp; ++i) integral_K[i] +=  GK_w[j]*v[k][i];
		}
		
		for(int i=0; i<ncomp; ++i){
			integral_G[i] *= (b-a)*0.5;
			integral_K[i] *= (b-a)*0.5;
			double diff2 = abs(integral_G[i]-integral_K[i]);
			if(diff2 > err) err = diff2;
		}
		err = err*sqrt(err)*200.0;
	}
};





namespace std
{
	template<typename T>
	struct less<Integrator_GK_region<T> >{
		bool operator()(const Integrator_GK_region<T> &x, const Integrator_GK_region<T> &y) const{
			if(x.err > y.err) return true; // we want the regions in the order of decreasing error
			else if(x.err < y.err) return false;
			else if(x.a < y.a) return true;
			else return false;
		}
	};
}






template <typename T>
struct Integrator{
	T& integrand;
	double accur; // precision
	vector<double> value; // result
	
	Integrator(T &f, double _accur) : integrand(f), accur(_accur){
		value.resize(integrand.ncomp);
	}
	
	void reset(){
		to_zero<T>(value);
	}
	
	/**
	 Performs a one-dimensional integral of a multi-component integrand
	 @param a		lower bound
	 @param b		upper bound
	 */
	void gauss_kronrod(double a, double b){
		
		int ncomp = (int)integrand.ncomp;
		const int min_regions = global_int("GK_min_regions");
		const int max_regions = 2000;
		set<Integrator_GK_region<T> > regions;
		
		// start by defining a minimum number of integration regions
		double L = (b-a)/min_regions;
		for(size_t i=0; i<min_regions; i++){
			regions.insert(Integrator_GK_region<T>(a+i*L,a+(i+1)*L, integrand));
		}
		
		// then iterate until the total error fits into the bounds
		
		while(true){
			double total_error = 0.0;
			for(auto& x : regions) total_error += x.err*x.err;
			total_error = sqrt(total_error);
			
			if(total_error < accur or regions.size() >= max_regions) break;
			
			// subdivide the regions with the largest error
			auto it = regions.begin();
			double ap = it->a;
			double bp = it->b;
			regions.erase(it);
			regions.insert(Integrator_GK_region<T>(ap, 0.5*(ap+bp), integrand));
			regions.insert(Integrator_GK_region<T>(0.5*(ap+bp), bp, integrand));
			if(global_bool("verb_integrals")) cout << "subdivide interval (" << ap << "," << bp << "), total error = " << total_error << endl;
		}
		if(regions.size() == max_regions) cout << "warning: max. number of integration regions exceeded" << endl;
		for(auto& x : regions){
			for(int i=0; i<ncomp; i++) value[i] += x.value[i];
		}
	}
};







template <typename T>
struct frequency_integrator{
	T& integrand;
	double accur; // precision
	vector<double> value; // result
	
	struct inverse_integrand{
		T& integrand;
		size_t ncomp;

		inverse_integrand(T& f) : integrand(f), ncomp(f.ncomp) {}
		
		void operator() (double iw, vector<double> &v)
		{
			double w = 1.0/iw;
			double ww = w*w;
			integrand(w,v);
			for(auto& x: v) x *= ww;
		}

	};
	
	frequency_integrator(T &f, double _accur) : integrand(f), accur(_accur){
		value.resize(integrand.ncomp);
	}
	
	void reset(){
		to_zero<T>(value);
	}

	
	/**
	 Performs an integral along the imaginary frequency axis
	 */
	void integrate(){
    double large_scale = global_double("large_scale");
		Integrator<T> direct_integral(integrand,accur);
		direct_integral.gauss_kronrod(-large_scale, large_scale);
		inverse_integrand the_inverse_integrand(integrand);
		Integrator<inverse_integrand> inverse_integral(the_inverse_integrand,accur);
		inverse_integral.gauss_kronrod(-1.0/large_scale, 0.0);
		inverse_integral.gauss_kronrod(0.0, 1.0/large_scale);
		value += direct_integral.value;
		value += inverse_integral.value;
		value *= 1.0/(2*M_PI);
	}

};

#endif
