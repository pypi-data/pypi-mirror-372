#ifndef HS_one_body_operator_h
#define HS_one_body_operator_h

#include "HS_nondiagonal_operator.hpp"

//! One-body operator acting in a given sector of the Hilbert space
template<typename HS_field>
struct HS_one_body_operator : HS_nondiagonal_operator<HS_field>
{
  template<typename op_field>
  HS_one_body_operator(shared_ptr<model> _the_model, const string &_name, sector _sec, const vector<matrix_element<op_field>> &elements)
  : HS_nondiagonal_operator<HS_field>(_the_model, _name, _sec)
  {
    check_signals();
    
    shared_ptr<symmetry_group> group = this->B->group;
    HS_field X;
    size_t n = group->N;
    
    for(size_t I=0; I<this->B->dim; ++I){ // loop over basis states
      binary_state ss = this->B->bin(I);// binary form of 'in' state
      auto R = group->Representative(ss,this->B->sec.irrep); // used to compute the number 'length' of terms in the symmetrized 'in' state
      for(auto &x : elements){ // loop over matrix elements of the 1-body operator
        if(x.r != x.c){ // if nondiagonal element
          binary_state ssp(ss); // binary state obtained by applying the matrix element to the state 'ss'
          int pauli_phase = ssp.one_body(binary_state::mask(x.c,n), binary_state::mask(x.r,n)); // computes ssp from ss, with phase
          if(pauli_phase==0) continue; // the hopping is impossible because of the Pauli principle
          auto Rp = group->Representative(ssp, this->B->sec.irrep); // finds the representative of the 'out' state
          size_t J = this->B->index(Rp.b); // finds the index of the 'out' state
          if(J==this->B->dim) continue; // not a valid state in this representation
          X = group->phaseX<HS_field>(Rp.phase) * fold_type<HS_field, op_field>(x.v) * (pauli_phase * sqrt((1.0*R.length)/Rp.length));
          this->insert(J,I,X); // inserts in the sparse matrix
                              // no need to add the Hermitean conjugate here, this is done in t
        }
        else if(ss.b&binary_state::mask(x.r,n)) this->insert(I, I, real(x.v)); // diagonal case
      }
    }
    this->sort_elements();
  }
};

#endif