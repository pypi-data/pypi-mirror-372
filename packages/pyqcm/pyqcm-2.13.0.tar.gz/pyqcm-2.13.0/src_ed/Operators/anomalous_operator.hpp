#ifndef anomalous_operator_h
#define anomalous_operator_h

#include "Hermitian_operator.hpp"
#include "HS_anomalous_operator.hpp"

//! Represents a pairing operator. op_field is meant to be either "double" or "complex<double>".
template<typename op_field>
struct anomalous_operator : Hermitian_operator
{
  bool spin_flip; //!< true if Nambu doubling is required (i.e., x or y component of the triplet d-vector)
  vector<matrix_element<op_field>> elements; //!< one-body matrix elements
  matrix<op_field> e; //!< dense one-body matrix (anomalous sector only)
  matrix<op_field> E; //!< dense one-body matrix, but within the mixing state of the model (may be extended)

  anomalous_operator(const string &_name, shared_ptr<model> the_model, const vector<matrix_element<op_field>>& _elements);
  void check_spin_flip();
  void set_target(vector<bool> &in_bath);
  void set_hopping_matrix(double value, matrix<double>& tc, bool spin_down, int sys_mixing);
  void set_hopping_matrix(double value, matrix<Complex>& tc, bool spin_down, int sys_mixing);
  double average_from_GF(matrix<Complex>& Gave, bool spin_down);
  shared_ptr<HS_Hermitian_operator> build_HS_operator(sector sec, bool complex_HS_op);
  void print(ostream& fout);
  
  template<typename HS_field>
  void set_hopping_matrix_templ(double value, matrix<HS_field>& tc, bool spin_down, int sys_mixing);
  vector<matrix_element<Complex>> matrix_elements();
  string type() {return string("anomalous");}
  void multiply_add_OTF(const vector<double> &x, vector<double> &y, double z, shared_ptr<ED_mixed_basis> B);
  void multiply_add_OTF(const vector<Complex> &x, vector<Complex> &y, double z, shared_ptr<ED_mixed_basis> B);
};

  
//==============================================================================
// implementation of anomalous_operator
  

  
/**
 Constructor from name and matrix elements
 @param _name   name of the operator
 @param _the_model   model
 @param _elements   nonzero one-body matrix elements
 */
template<typename op_field>
anomalous_operator<op_field>::anomalous_operator(const string &_name, shared_ptr<model> _the_model,  const vector<matrix_element<op_field>>& _elements) :
Hermitian_operator(_name, _the_model)
{
  if(typeid(op_field) == typeid(Complex)) is_complex = true;
  mixing |= HS_mixing::anomalous;
  // fixes the matrix elements regarding antisymmetry
  elements.clear();
  elements.reserve(_elements.size());
  for(auto& x : _elements){
    if(x.r < x.c){  // It is important to keep this in place because of the way lattice anomalous operators are defined!!!
      elements.push_back(matrix_element<op_field>(x.r, x.c, x.v));
      elements.push_back(matrix_element<op_field>(x.c, x.r, -x.v));
    }
  }

  if (elements.size() == 0) qcm_ED_throw("building empty anomalous operator.");

  check_spin_flip(); // checks whether the operator has triplet terms that require Nambu doubling
  set_target(the_model->in_bath); // sets the target (1,2 or 3) of the operator

  // building the temporary element map
  map<index_pair, op_field> element_map; //!< temporary map form of elements, for checks
  for(auto& x : elements) element_map[{x.r, x.c}] = x.v;
  the_model->group->check_invariance<op_field>(element_map, name, false);
  element_map.clear();
  
  // constructing the full matrix e (but still off diagonal, i.e., Nambu - nonNambu)
  size_t ns = the_model->n_sites;
  size_t nb = the_model->n_bath;
  size_t no = the_model->n_orb;
  matrix<op_field> M(2*the_model->n_orb); // full matrix, independent of mixing, but still off diagonal
  for(auto& x : elements) M(x.r, x.c) += x.v;
  
  switch(target){
    case 1: // cluster only
      e.set_size(2*ns);
      M.move_sub_matrix(ns, ns, 0, 0, 0, 0, e);
      M.move_sub_matrix(ns, ns, no, no, ns, ns, e);
      M.move_sub_matrix(ns, ns, 0, no, 0, ns, e);
      M.move_sub_matrix(ns, ns, no, 0, ns, 0, e);
      break;
      
    case 2: // bath only
      e.set_size(2*nb);
      M.move_sub_matrix(nb, nb, ns, ns, 0, 0, e);
      M.move_sub_matrix(nb, nb, no+ns, no+ns, nb, nb, e);
      M.move_sub_matrix(nb, nb, ns, no+ns, 0, nb, e);
      M.move_sub_matrix(nb, nb, ns+no, ns, nb, 0, e);
      break;
      
    case 3: // cluster-bath hybridization
      e.set_size(2*ns, 2*nb);
      M.move_sub_matrix(ns, nb, 0, ns, 0, 0, e);
      M.move_sub_matrix(ns, nb, no, no+ns, ns, nb, e);
      M.move_sub_matrix(ns, nb, 0, no+ns, 0, nb, e);
      M.move_sub_matrix(ns, nb, no, ns, ns, 0, e);
      break;
  }
}




/**
 determines whether the operator has spin-flip/triplet terms
 sets the bool variable spin_flip accordingly
 Since this is an pairing operator, 'spin flip' occurs when there are triplet terms, i.e. terms that couple
 the same spin!
 */
template<typename op_field>
void anomalous_operator<op_field>::check_spin_flip()
{
  for(auto &S : elements){
    if((S.r < the_model->n_orb and S.c < the_model->n_orb) or (S.r >= the_model->n_orb and S.c >= the_model->n_orb)){
      mixing |= HS_mixing::spin_flip;
      break;
    }
  }
}



/**
 set the target of an operator
 1 : cluster
 2 : bath only
 3 : hybridization
 @param in_bath vector of bool defining the status of each site
 */
template<typename op_field>
void anomalous_operator<op_field>::set_target(vector<bool> &in_bath){
  
  if(in_bath[this->elements[0].r]){
    if(in_bath[this->elements[0].c]) this->target = 2;
    else this->target = 3;
  }
  
  else{
    if(in_bath[this->elements[0].c]) this->target = 3;
    else this->target = 1;
  }
  
  if(this->target==1){
    for(auto& x : this->elements){
      if(in_bath[x.r] or in_bath[x.c])
        qcm_ED_throw("operator "+this->name+" has no unique target");
    }
  }
  
  else if(this->target==2){
    for(auto& x : this->elements){
      if(!in_bath[x.r] or !in_bath[x.c])
        qcm_ED_throw("operator "+this->name+" has no unique target");
    }
  }
  
  else{
    for(auto& x : this->elements){
      if(in_bath[x.r] == in_bath[x.c]) qcm_ED_throw("operator "+this->name+" has no unique target");
    }
  }
}




/**
Computes the average of the operator in an uncorrelated ground state, determined solely by the average
of the uncorrelated Green function
 */ 
template<typename op_field>
double anomalous_operator<op_field>::average_from_GF(matrix<Complex>& Gave, bool spin_down)
{
  matrix<Complex> Efull(Gave.r);
  int d = Gave.c - E.c;

  switch(target){
    case 1:
      E.move_sub_matrix(E.r,E.c,0,0,0,0,Efull);
      break;
    case 2:
      E.move_sub_matrix(E.r,E.c,0,0,d,d,Efull);
      break;
    case 3:
      E.move_sub_matrix(E.r,E.c,0,0,0,d,Efull);
      E.move_sub_matrix_HC(E.r,E.c,0,0,d,0,Efull);
      break;
  }

  Complex z = Gave.trace_product(Efull, true);
  return real(z);
}


/**
 returns a pointer to, and constructs the associated HS operator in the sector sec.
 @param sec : sector of the Hilbert space
 @param complex_HS_op : true if the Hilbert space is complex
 */
template<typename op_field>
shared_ptr<HS_Hermitian_operator> anomalous_operator<op_field>::build_HS_operator(sector sec, bool complex_HS_op)
{
  shared_ptr<ED_mixed_basis> B = the_model->provide_basis(sec);
  if(complex_HS_op) return make_shared<HS_anomalous_operator<Complex>>(the_model, name, sec, elements);
  else return make_shared<HS_anomalous_operator<double>>(the_model, name, sec, elements);
}




/**
 Adds the contribution of the operator to the 1-body matrices \a tc, \a tb and \a tcb
 @param value : value of the matrix element
 @param tc : 1-body matrix the operator contributes to
 @param spin_down : true in the spin-down case of mixing=4
 @param sys_mixing : mixing state of the model (not that of the operator)
 */
template<>
inline void anomalous_operator<double>::set_hopping_matrix(double value, matrix<double>& tc, bool spin_down, int sys_mixing)
{
  set_hopping_matrix_templ<double>(value, tc, spin_down, sys_mixing);
}
template<>
inline void anomalous_operator<Complex>::set_hopping_matrix(double value, matrix<double>& tc, bool spin_down, int sys_mixing)
{
  qcm_ED_throw("a complex-valued operator (anomalous) cannot contribute to a real hopping matrix!");
}
template<typename op_field>
inline void anomalous_operator<op_field>::set_hopping_matrix(double value, matrix<Complex>& tc, bool spin_down, int sys_mixing)
{
  set_hopping_matrix_templ<Complex>(value, tc, spin_down, sys_mixing);
}



template<typename op_field>
template<typename HS_field>
void anomalous_operator<op_field>::set_hopping_matrix_templ(double value, matrix<HS_field>& tc, bool spin_down, int sys_mixing)
{
  E.set_size(tc.r, tc.c);

  size_t nR=0, nC=0;
  switch(target){
    case 1: // in cluster
      nR = nC = the_model->n_sites;
      break;
    case 2: // in bath
      nR = nC = the_model->n_bath;
      break;
    case 3: // hybrid
      nC = the_model->n_bath;
      nR = the_model->n_sites;
      break;
  }
  switch(sys_mixing){
    case HS_mixing::anomalous:
      if(target!=3){
        e.move_sub_matrix(nR, nC, nR, 0, nR, 0, E, 2.0);
        e.move_sub_matrix_HC(nR, nC, nR, 0, 0, nC, E, 2.0);
      }
      else{
        e.move_sub_matrix(nR, nC, nR, 0, nR, 0, E, 2.0);
        e.move_sub_matrix_conjugate(nR, nC, 0, nC, 0, nC, E, -2.0); // BUG FIX 2021-11-29 
      }
      break;
      
    case HS_mixing::full :
      if(target!=3){
        e.move_sub_matrix(2*nR, 2*nC, 0, 0, 2*nR, 0, E, 2.0);
        e.move_sub_matrix_HC(2*nR, 2*nC, 0, 0, 0, 2*nC, E, 2.0);
      }
      else{
        e.move_sub_matrix(2*nR, 2*nC, 0, 0, 2*nR, 0, E, 2.0);
        e.move_sub_matrix_conjugate(2*nR, 2*nC, 0, 0, 0, 2*nC, E, -2.0);
      }
      break;
  }
  tc.v += (E.v*value);
}




/**
 prints definition to a file
 @param fout output stream
 */
template<typename op_field>
void anomalous_operator<op_field>::print(ostream& fout)
{
  fout << "\nanomalous operator " << name << "\t (mixing " << mixing << ")" << endl;;
  for(auto& x : elements) fout << x.r+1 << '\t' << x.c+1 << '\t' << x.v << endl;
}




/**
 returns a list of complexified matrix elements
 */
template<typename op_field>
vector<matrix_element<Complex>> anomalous_operator<op_field>::matrix_elements()
{
  vector<matrix_element<Complex>> celem(elements.size());
  for(int i=0; i<elements.size(); i++){
    auto el = elements[i];
    celem[i] = {el.r, el.c, Complex(el.v)};
  }
  return celem;
}



/**
Applies the HS operator associated to the anomalous operator in the basis B to state vector x and adds the result to state vector y,
by computing the matrix elements "on the fly" (OTF). This is used in the "onthefly" option of the Hamiltonian format.
This is the version for a real Hilbert space
*/
template<typename op_field>
void anomalous_operator<op_field>::multiply_add_OTF(const vector<double> &x, vector<double> &y, double z, shared_ptr<ED_mixed_basis> B)
{
  if(typeid(op_field)==typeid(Complex)) qcm_ED_throw("A complex operator cannot lead to a real HS operator!");
  
  double X;
  size_t n = B->L;
  
  for(size_t I=0; I<B->dim; ++I){ // loop over basis states
    binary_state ss = B->bin(I);// binary form of 'in' state
    for(auto &E : elements){ // loop over matrix elements of the 1-body operator
      if(E.c > E.r) continue;  // r > c important
      if(E.r != E.c){ // if nondiagonal element
        binary_state ssp(ss); // binary state obtained by applying the matrix element to the state 'ss'
        int pauli_phase = ssp.pair_annihilate(binary_state::mask(E.c,n), binary_state::mask(E.r,n)); // computes ssp from ss, with phase
        if(pauli_phase==0) continue; // the hopping is impossible because of the Pauli principle
        size_t J = B->index(ssp); // finds the index of the 'out' state
        if(J==B->dim) continue; // not a valid state in this representation
        X = 2*z*pauli_phase*real(E.v);
        y[I] += X*x[J];
        y[J] += conjugate(X)*x[I];
      }
      else if(ss.b&binary_state::mask(E.r,n)) y[I] += z*real(E.v)*x[I]; // diagonal case
    }
  }
}
/**
Applies the HS operator associated to the anomalous operator in the basis B to state vector x and adds the result to state vector y,
by computing the matrix elements "on the fly" (OTF). This is used in the "onthefly" option of the Hamiltonian format.
This is the version for a complex Hilbert space
*/
template<typename op_field>
void anomalous_operator<op_field>::multiply_add_OTF(const vector<Complex> &x, vector<Complex> &y, double z, shared_ptr<ED_mixed_basis> B)
{  
  Complex X;
  size_t n = B->L;
  
  for(size_t I=0; I<B->dim; ++I){ // loop over basis states
    binary_state ss = B->bin(I);// binary form of 'in' state
    for(auto &E : elements){ // loop over matrix elements of the 1-body operator
      if(E.c > E.r) continue;  // r > c important
      if(E.r != E.c){ // if nondiagonal element
        binary_state ssp(ss); // binary state obtained by applying the matrix element to the state 'ss'
        int pauli_phase = ssp.pair_annihilate(binary_state::mask(E.c,n), binary_state::mask(E.r,n)); // computes ssp from ss, with phase
        if(pauli_phase==0) continue; // the hopping is impossible because of the Pauli principle
        size_t J = B->index(ssp); // finds the index of the 'out' state
        if(J==B->dim) continue; // not a valid state in this representation
        X = (2*z*pauli_phase)*E.v;
        y[I] += X*x[J];
        y[J] += conjugate(X)*x[I];
      }
      else if(ss.b&binary_state::mask(E.r,n)) y[I] += z*E.v*x[I]; // diagonal case
    }
  }
}


#endif
