#ifndef HS_Hund_operator_h
#define HS_Hund_operator_h

#include "HS_nondiagonal_operator.hpp"

//! Represents a Hund operator in a sector of the Hilbert space
template<typename HS_field>
struct HS_Hund_operator : HS_nondiagonal_operator<HS_field>
{
  HS_Hund_operator(shared_ptr<model> _the_model, const string &_name, sector _sec, const vector<matrix_element<double>> &elements)
  : HS_nondiagonal_operator<HS_field>(_the_model, _name, _sec)
  {
    ED_mixed_basis& B = *this->B;
    shared_ptr<symmetry_group> group = B.group;
    HS_field X;
    size_t n = group->N;
    
    for(auto &x : elements){
      // create a list of masks for pair creation and annihilation
      uint64_t mask_n[2]; // occupation masks
      
      mask_n[0] = binary_state::mask(x.r,n) + binary_state::mask(x.c,n);
      mask_n[1] = binary_state::mask(x.r+n,n) + binary_state::mask(x.c+n,n);
      size_t P[2] = {x.r, x.c};
      
      // loop over states
      for(size_t I=0; I<B.dim; ++I){
        
        // diagonal terms (note the minus sign of the contribution)
        if((B.bin(I).b & mask_n[0]) == mask_n[0]) this->insert(I,I,-x.v);
        if((B.bin(I).b & mask_n[1]) == mask_n[1]) this->insert(I,I,-x.v);
        
        int pauli_phase;
        binary_state ssp;
        
        binary_state ss = B.bin(I);// binary form of state 'label'
        auto R = group->Representative(ss, B.sec.irrep);
        
        for(int Pu = 0; Pu<2; Pu++){
          for(int Pd = 0; Pd<2; Pd++){
            ssp = ss;
            pauli_phase = ssp.one_body(binary_state::mask(P[Pu],n), binary_state::mask(P[(Pu+1)%2],n));
            pauli_phase *= ssp.one_body(binary_state::mask(P[Pd]+n,n), binary_state::mask(P[(Pd+1)%2]+n,n));
            if(pauli_phase!=0){
              auto Rp = group->Representative(ssp, B.sec.irrep);
              int J = B.index(Rp.b); // finds the index of the 'out' state
              if(J<B.dim) {
                // finding the phase
                X = group->phaseX<HS_field>(Rp.phase) *  x.v * (pauli_phase * sqrt((1.0*R.length)/Rp.length));
                this->insert(J,I,X);
              }
            }
          }
        }
      }
    }
    this->sort_elements();
  }
};


#endif /* Hund_operator_h */
