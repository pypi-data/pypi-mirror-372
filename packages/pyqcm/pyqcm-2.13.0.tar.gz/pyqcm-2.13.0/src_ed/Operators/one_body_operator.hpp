#ifndef one_body_operator_h
#define one_body_operator_h

#include "Hermitian_operator.hpp"
#include "HS_factorized_operator.hpp"
#include "HS_one_body_operator.hpp"

//! one-body operator
template<typename op_field>
struct one_body_operator : Hermitian_operator
{
  bool spin_flip;
  
  vector<matrix_element<op_field>> elements; //!< matrix elements
  matrix<op_field> e;
  matrix<op_field> e_down;
  matrix<op_field> E;
  matrix<op_field> E_down;
  map<index_pair, op_field> element_map; //!< temporary map form of elements, for checks
  map<int, shared_ptr<HS_half_operator<op_field>>> half_operators; //!< Hilbert space realizations, organized by particle number
  map<int, shared_ptr<HS_half_operator<op_field>>> half_operators_dw; //!< the same, for the spin_down part, if different

  one_body_operator(const string &_name, shared_ptr<model> the_model, const vector<matrix_element<op_field>>& _elements);
  void check_Hermiticity();
  void check_spin_flip();
  void check_spin_symmetry();
  void set_target(vector<bool> &in_bath);
  void set_hopping_matrix(double value, matrix<double>& tc, bool spin_down, int sys_mixing);
  void set_hopping_matrix(double value, matrix<Complex>& tc, bool spin_down, int sys_mixing);
  double average_from_GF(matrix<Complex>& Gave, bool spin_down);
 
  shared_ptr<HS_Hermitian_operator> build_HS_operator(sector sec, bool complex_HS_op);
  void print(ostream& fout);

  template<typename HS_field>
  void set_hopping_matrix_templ(double value, matrix<HS_field>& tc, bool spin_down, int sys_mixing);

  vector<matrix_element<Complex>> matrix_elements();
  string type() {return string("one_body");}

  void multiply_add_OTF(const vector<double> &x, vector<double> &y, double z, shared_ptr<ED_mixed_basis> B);
  void multiply_add_OTF(const vector<Complex> &x, vector<Complex> &y, double z, shared_ptr<ED_mixed_basis> B);

};




//==============================================================================
// implementation


/**
 Constructor from name and matrix elements
 @param _name   name of the operator
 @param _the_model   model
 @param _elements   nonzero one-body matrix elements
 */
template<typename op_field>
one_body_operator<op_field>::one_body_operator(const string &_name, shared_ptr<model> _the_model, const vector<matrix_element<op_field>>& _elements)
: Hermitian_operator(_name, _the_model)
{

  if(typeid(op_field) == typeid(Complex)) is_complex = true;
  is_factorizable = true;
  
  // fixes the matrix elements regarding hermiticity
  elements.clear();
  elements.reserve(_elements.size());
  for(auto& x : _elements){
    if(x.r < x.c){
      elements.push_back(matrix_element<op_field>(x.r, x.c, x.v));
      elements.push_back(matrix_element<op_field>(x.c, x.r, conjugate(x.v)));
    }
    else if (x.r == x.c) elements.push_back(matrix_element<op_field>(x.r, x.c, x.v));
  }

  
  for(auto& x : elements) element_map[{x.r, x.c}] = x.v;

  check_Hermiticity();
  check_spin_flip();
  check_spin_symmetry();
  the_model->group->check_invariance<op_field>(element_map, name, false);
  element_map.clear();
  
  set_target(the_model->in_bath);
  
  // constructing the full matrix e
  size_t ns = the_model->n_sites;
  size_t nb = the_model->n_bath;
  size_t no = the_model->n_orb;
  matrix<op_field> M(2*the_model->n_orb);
  for(auto& x : elements) M(x.r, x.c) += x.v;

  // computing the Nambu correction
  if(target != 3){
    for(auto& x : elements){
      if(x.r==x.c){
        nambu_correction_full += real(x.v);
        if(x.r < no) nambu_correction += real(x.v);
      }  
    }  
  }

  
  switch(target){
    case 1:
      if(mixing == HS_mixing::normal){
        e.set_size(ns);
        M.move_sub_matrix(ns,ns,0,0,0,0,e);
      }
      else if(mixing == HS_mixing::spin_flip){
        e.set_size(2*ns);
        M.move_sub_matrix(ns,ns,0,0,0,0,e);
        M.move_sub_matrix(ns,ns,no,no,ns,ns,e);
        M.move_sub_matrix(ns,ns,0,no,0,ns,e);
        M.move_sub_matrix(ns,ns,no,0,ns,0,e);
      }
      else if(mixing == HS_mixing::up_down){
        e.set_size(ns);
        M.move_sub_matrix(ns,ns,0,0,0,0,e);
        e_down.set_size(ns);
        M.move_sub_matrix(ns,ns,no,no,0,0,e_down);
      }
      break;

    case 2:
      if(mixing == HS_mixing::normal){
        e.set_size(nb);
        M.move_sub_matrix(nb,nb,ns,ns,0,0,e);
      }
      else if(mixing == HS_mixing::spin_flip){
        e.set_size(2*nb);
        M.move_sub_matrix(nb,nb,ns,ns,0,0,e);
        M.move_sub_matrix(nb,nb,no+ns,no+ns,nb,nb,e);
        M.move_sub_matrix(nb,nb,ns,no+ns,0,nb,e);
        M.move_sub_matrix(nb,nb,ns+no,ns,nb,0,e);
      }
      else if(mixing == HS_mixing::up_down){
        e.set_size(nb);
        M.move_sub_matrix(nb,nb,ns,ns,0,0,e);
        e_down.set_size(nb);
        M.move_sub_matrix(nb,nb,no+ns,no+ns,0,0,e_down);
      }
      break;

    case 3:
      if(mixing == HS_mixing::normal){
        e.set_size(the_model->n_sites, the_model->n_bath);
        M.move_sub_matrix(ns,nb,0,ns,0,0,e);
      }
      else if(mixing == HS_mixing::spin_flip){
        e.set_size(2*the_model->n_sites, 2*the_model->n_bath);
        M.move_sub_matrix(ns,nb,0,ns,0,0,e);
        M.move_sub_matrix(ns,nb,no,no+ns,ns,nb,e);
        M.move_sub_matrix(ns,nb,0,no+ns,0,nb,e);
        M.move_sub_matrix(ns,nb,no,ns,ns,0,e);
      }
      else if(mixing == HS_mixing::up_down){
        e.set_size(the_model->n_sites, the_model->n_bath);
        M.move_sub_matrix(ns,nb,0,ns,0,0,e);
        e_down.set_size(the_model->n_sites, the_model->n_bath);
        M.move_sub_matrix(ns,nb,no,ns+no,0,0,e_down);
      }
      break;
  }
}






/**
 checks whether the list of elements is Hermitian
 */
template<typename op_field>
void one_body_operator<op_field>::check_Hermiticity()
{
  for(auto &S : element_map){
    if(element_map.find({S.first.c, S.first.r}) == element_map.end())
      qcm_ED_throw("element ("+to_string(S.first.c)+','+to_string(S.first.r)+") of "+name+" should exist by Hermiticity");
    op_field z = conjugate(S.second) - element_map.at({S.first.c, S.first.r});
    if(abs(z) > SMALL_VALUE)
      qcm_ED_throw("operator "+name+" is not Hermitian");
  }
}




/**
 determines whether the operator has spin-flip terms
 sets the bool variable spin_flip accordingly
 */
template<typename op_field>
void one_body_operator<op_field>::check_spin_flip()
{
  for(auto &S : elements){
    if((S.r < the_model->n_orb and S.c >= the_model->n_orb) or (S.r >= the_model->n_orb and S.c < the_model->n_orb)){
      mixing |= HS_mixing::spin_flip; // bitwise OR
      break;
    }
  }
}




/**
 determines whether the operator is symmetric under the exchange of up and down spins
 */
template<typename op_field>
void one_body_operator<op_field>::check_spin_symmetry()
{
  if(mixing&HS_mixing::spin_flip) return;

  for(auto &x : element_map){
    index_pair p = x.first;
    if(p.r < the_model->n_orb) p.r += the_model->n_orb;
    else p.r -= the_model->n_orb;
    if(p.c < the_model->n_orb) p.c += the_model->n_orb;
    else p.c -= the_model->n_orb;
    auto y = element_map.find(p);
    if(y == element_map.end() or y->second != x.second){
      mixing |= HS_mixing::up_down; // bitwise OR
      break;
    };
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
void one_body_operator<op_field>::set_target(vector<bool> &in_bath){
  
  if(in_bath[elements[0].r]){
    if(in_bath[elements[0].c]) this->target = 2;
    else this->target = 3;
  }
  
  else{
    if(in_bath[elements[0].c]) this->target = 3;
    else this->target = 1;
  }
  
  if(this->target==1){
    for(auto& x : elements){
      if(in_bath[x.r] or in_bath[x.c])
        qcm_ED_throw("operator "+this->name+" has no unique target");
    }
  }
  
  else if(this->target==2){
    for(auto& x : elements){
      if(!in_bath[x.r] or !in_bath[x.c])
        qcm_ED_throw("operator "+this->name+" has no unique target");
    }
  }
  
  else{
    for(auto& x : elements){
      if(in_bath[x.r] == in_bath[x.c])
        qcm_ED_throw("operator "+this->name+" has no unique target");
    }
  }
}






/**
 returns a pointer to, and constructs the associated HS operator in the sector with basis B.
 */
template<typename op_field>
shared_ptr<HS_Hermitian_operator> one_body_operator<op_field>::build_HS_operator(sector sec, bool complex_HS_op)
{
  if(the_model->is_factorized){
    return make_shared<HS_factorized_operator<op_field>>(the_model, name, sec, this);
  }
  else{
    if(complex_HS_op or is_complex) return make_shared<HS_one_body_operator<Complex>>(the_model, name, sec, elements);
    else return make_shared<HS_one_body_operator<double>>(the_model, name, sec, elements);
  }
}


/**
 Adds the contribution of the operator to the matrices \a tc, \a tb or \a tcb
*/
template<>
inline void one_body_operator<double>::set_hopping_matrix(double value, matrix<double>& tc, bool spin_down, int sys_mixing)
{
  // if(fabs(value) < SMALL_VALUE) return;
  set_hopping_matrix_templ<double>(value, tc, spin_down, sys_mixing);
}
template<>
inline void one_body_operator<Complex>::set_hopping_matrix(double value, matrix<double>& tc, bool spin_down, int sys_mixing)
{
  // if(fabs(value) < SMALL_VALUE) return;
  qcm_ED_throw("a complex-valued operator cannot contribute to a real hopping matrix!");
}
template<typename HilbertField>
inline void one_body_operator<HilbertField>::set_hopping_matrix(double value, matrix<Complex>& tc, bool spin_down, int sys_mixing)
{
  set_hopping_matrix_templ<Complex>(value, tc, spin_down, sys_mixing);
}



template<typename op_field>
template<typename HS_field>
void one_body_operator<op_field>::set_hopping_matrix_templ(double value, matrix<HS_field>& tc, bool spin_down, int sys_mixing)
{
  matrix<op_field>& EE = spin_down? E_down : E;
  EE.set_size(tc.r, tc.c);

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
    case HS_mixing::normal :
      e.move_sub_matrix(nR,nC,0,0,0,0,EE);
      break;
    case HS_mixing::up_down :
      if(spin_down and mixing==HS_mixing::up_down) e_down.move_sub_matrix(nR,nC,0,0,0,0,EE);
      else e.move_sub_matrix(nR,nC,0,0,0,0,EE);
      break;
      
    case HS_mixing::anomalous:
      if(mixing==HS_mixing::normal){
        e.move_sub_matrix(nR,nC,0,0,0,0,EE);
        if(target==3) e.move_sub_matrix_conjugate(nR,nC,0,0,nR,nC,EE,-1);  // attention
        else e.move_sub_matrix_transpose(nR,nC,0,0,nR,nC,EE,-1);
      }
      else if(mixing==HS_mixing::up_down){
        e.move_sub_matrix(nR,nC,0,0,0,0,EE);
        if(target==3) e_down.move_sub_matrix_conjugate(nR,nC,0,0,nR,nC,EE,-1); // devrait être conjugate pour target = 3 (hybridation)
        else e_down.move_sub_matrix_transpose(nR,nC,0,0,nR,nC,EE,-1);
      }
      break;
      
    case HS_mixing::spin_flip :
      if(mixing==HS_mixing::normal){
        e.move_sub_matrix(nR,nC,0,0,0,0,EE);
        e.move_sub_matrix(nR,nC,0,0,nR,nC,EE);
      }
      else if(mixing==HS_mixing::spin_flip){
        e.move_sub_matrix(2*nR,2*nC,0,0,0,0,EE);
      }
      else if(mixing==HS_mixing::up_down){
        e.move_sub_matrix(nR,nC,0,0,0,0,EE);
        e_down.move_sub_matrix(nR,nC,0,0,nR,nC,EE);
      }
      break;
      
    case HS_mixing::full :
      if(mixing==HS_mixing::normal){
        e.move_sub_matrix(nR,nC,0,0,0,0,EE);
        e.move_sub_matrix(nR,nC,0,0,nR,nC,EE);
        if(target==3) {
          e.move_sub_matrix_conjugate(nR,nC,0,0,2*nR,2*nC,EE,-1); // attention
          e.move_sub_matrix_conjugate(nR,nC,0,0,3*nR,3*nC,EE,-1); // attention
        }
        else{
          e.move_sub_matrix_transpose(nR,nC,0,0,2*nR,2*nC,EE,-1); // attention
          e.move_sub_matrix_transpose(nR,nC,0,0,3*nR,3*nC,EE,-1); // attention
        }
      }
      else if(mixing&HS_mixing::up_down){
        e.move_sub_matrix(nR,nC,0,0,0,0,EE);
        e_down.move_sub_matrix(nR,nC,0,0,nR,nC,EE);
        if(target==3) {
          e.move_sub_matrix_conjugate(nR,nC,0,0,2*nR,2*nC,EE,-1);  // attention
          e_down.move_sub_matrix_conjugate(nR,nC,0,0,3*nR,3*nC,EE,-1);  // attention
        }
        else{
          e.move_sub_matrix_transpose(nR,nC,0,0,2*nR,2*nC,EE,-1);  // attention
          e_down.move_sub_matrix_transpose(nR,nC,0,0,3*nR,3*nC,EE,-1);  // attention
        }
      }
      else if(mixing==HS_mixing::spin_flip){
        e.move_sub_matrix(2*nR,2*nC,0,0,0,0,EE);
        if(target==3) e.move_sub_matrix_conjugate(2*nR,2*nC,0,0,2*nR,2*nC,EE,-1);  // attention
        else e.move_sub_matrix_transpose(2*nR,2*nC,0,0,2*nR,2*nC,EE,-1);  // attention
      }
      break;
  }
  tc.v += (EE.v*value);
}




template<typename op_field>
double one_body_operator<op_field>::average_from_GF(matrix<Complex>& Gave, bool spin_down)
{
  matrix<Complex> Efull(Gave.r);
  matrix<op_field>& EE = E;
  if(spin_down) EE = E_down;
  int d = Gave.c - EE.c;

  switch(target){
    case 1:
      EE.move_sub_matrix(EE.r,EE.c,0,0,0,0,Efull);
      break;
    case 2:
      EE.move_sub_matrix(EE.r,EE.c,0,0,d,d,Efull);
      break;
    case 3:
      EE.move_sub_matrix(EE.r,EE.c,0,0,0,d,Efull);
      EE.move_sub_matrix_HC(EE.r,EE.c,0,0,d,0,Efull);
      break;
  }

  Complex z = Gave.trace_product(Efull, true);
  return real(z);
}



/**
 prints definition to a file
 @param fout output stream
 */
template<typename op_field>
void one_body_operator<op_field>::print(ostream& fout)
{
  fout << "\none-body operator " << name << "\t (mixing " << mixing << ", target " << target << ")" << endl;
  for(auto& x : elements) fout << x.r+1 << '\t' << x.c+1 << '\t' << x.v << endl;
}


/**
 returns a list of complexified matrix elements
 */
template<typename op_field>
vector<matrix_element<Complex>> one_body_operator<op_field>::matrix_elements()
{
  vector<matrix_element<Complex>> celem(elements.size());
  for(int i=0; i<elements.size(); i++){
    auto el = elements[i];
    celem[i] = {el.r, el.c, Complex(el.v)};
  }
  return celem;
}


template<typename op_field>
void one_body_operator<op_field>::multiply_add_OTF(const vector<double> &x, vector<double> &y, double z, shared_ptr<ED_mixed_basis> B)
{
  if(typeid(op_field)==typeid(Complex)) qcm_ED_throw("A complex operator cannot lead to a real HS operator!");
  
  double X;
  size_t n = B->L;
  
  for(size_t I=0; I<B->dim; ++I){ // loop over basis states
    binary_state ss = B->bin(I);// binary form of 'in' state
    for(auto &E : elements){ // loop over matrix elements of the 1-body operator
      if(E.r != E.c){ // if nondiagonal element
        binary_state ssp(ss); // binary state obtained by applying the matrix element to the state 'ss'
        int pauli_phase = ssp.one_body(binary_state::mask(E.c,n), binary_state::mask(E.r,n)); // computes ssp from ss, with phase
        if(pauli_phase==0) continue; // the hopping is impossible because of the Pauli principle
        size_t J = B->index(ssp); // finds the index of the 'out' state
        if(J==B->dim) continue; // not a valid state in this representation
        X = z*pauli_phase*real(E.v);
        y[J] += X*x[I];
      }
      else if(ss.b&binary_state::mask(E.r,n)) y[I] += z*real(E.v)*x[I]; // diagonal case
    }
  }
}
template<typename op_field>
void one_body_operator<op_field>::multiply_add_OTF(const vector<Complex> &x, vector<Complex> &y, double z, shared_ptr<ED_mixed_basis> B)
{  
  Complex X;
  size_t n = B->L;
  
  for(size_t I=0; I<B->dim; ++I){ // loop over basis states
    binary_state ss = B->bin(I);// binary form of 'in' state
    for(auto &E : elements){ // loop over matrix elements of the 1-body operator
      if(E.r != E.c){ // if nondiagonal element
        binary_state ssp(ss); // binary state obtained by applying the matrix element to the state 'ss'
        int pauli_phase = ssp.one_body(binary_state::mask(E.c,n), binary_state::mask(E.r,n)); // computes ssp from ss, with phase
        if(pauli_phase==0) continue; // the hopping is impossible because of the Pauli principle
        size_t J = B->index(ssp); // finds the index of the 'out' state
        if(J==B->dim) continue; // not a valid state in this representation
        X = (z*pauli_phase)*E.v;
        y[I] += conjugate(X)*x[J];
      }
      else if(ss.b&binary_state::mask(E.r,n)) y[I] += z*E.v*x[I]; // diagonal case
    }
  }
}



#endif /* one_body_operator_h */
