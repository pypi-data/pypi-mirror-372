#ifndef HS_anomalous_operator_h
#define HS_anomalous_operator_h

#include "HS_nondiagonal_operator.hpp"

//! Represents an anomalous operator in a sector of the Hilbert space
template<typename HS_field>
struct HS_anomalous_operator : HS_nondiagonal_operator<HS_field>
{
  template<typename op_field>
  HS_anomalous_operator(shared_ptr<model> _the_model, const string &_name, sector _sec, const vector<matrix_element<op_field>> &elements) : HS_nondiagonal_operator<HS_field>(_the_model, _name, _sec)

  {
    check_signals();
    shared_ptr<symmetry_group> group = this->B->group;

    HS_field X;
    size_t n = this->B->L;
    
    // loop over the states of the Hilbert space
    for(size_t I=0; I<this->B->dim; ++I){
      int length;
      int phase;
      binary_state ss = this->B->bin(I);// binary form of state labelled by I
      rep_map R = this->B->group->Representative(ss,this->B->sec.irrep);
      for(auto &x : elements){ // loop over elements of the 1-body operator
        if(x.c > x.r) continue;  // r > c important
        binary_state ssp(ss); // initializes the 'out' state = 'in' state
        // modifies the 'out' state by annihilating a pair
        int pauli_phase = ssp.pair_annihilate(binary_state::mask(x.r,n), binary_state::mask(x.c,n));
        if(pauli_phase==0) continue; // impossible to destroy pair; continue.
        // computes the representative label under point group
        rep_map Rp = this->B->group->Representative(ssp, this->B->sec.irrep);
        size_t J = this->B->index(Rp.b); // finds the index of the 'out' state
        if(J==this->B->dim) continue; // not a valid state in this representation
        X = 2.0 * group->phaseX<HS_field>(Rp.phase) * fold_type<HS_field, op_field>(x.v) * (pauli_phase * sqrt((1.0*R.length)/Rp.length));; // 2.0 because of the transpose of the antisymmetric delta
        this->insert(J,I,X);
        this->insert(I,J,conjugate(X)); // hermitian conjugate
      }
    }
    this->sort_elements(); // sorting the elements for faster application/translation into CSR matrix
  }
  
};

#endif
