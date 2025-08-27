#ifndef HS_Heisenberg_operator_h
#define HS_Heisenberg_operator_h

#include "HS_nondiagonal_operator.hpp"

//! Represents a Heisenberg operator in a sector of the Hilbert space
template<typename HS_field>
struct HS_Heisenberg_operator : HS_nondiagonal_operator<HS_field>
{
  HS_Heisenberg_operator(shared_ptr<model> _the_model, const string &_name, sector _sec, const vector<matrix_element<double>> &elements, char dir)
  : HS_nondiagonal_operator<HS_field>(_the_model, _name, _sec)
  {
    ED_mixed_basis& B = *this->B;
    shared_ptr<symmetry_group> group = B.group;
    HS_field X;
    size_t n = group->N;
    
    
    for(auto &x : elements){
      // create a list of masks for pair creation and annihilation
      uint64_t mask_n[4]; // occupation masks
      
      mask_n[0] = binary_state::mask(x.r,n) + binary_state::mask(x.c,n);
      mask_n[1] = binary_state::mask(x.r+n,n) + binary_state::mask(x.c+n,n);
      mask_n[2] = binary_state::mask(x.r,n) + binary_state::mask(x.c+n,n);
      mask_n[3] = binary_state::mask(x.r+n,n) + binary_state::mask(x.c,n);
      
      // diagonal terms (note the minus sign of the contribution)
      if(dir == 'H' or dir == 'Z'){
        // loop over states
        for(size_t I=0; I<B.dim; ++I){
          if((B.bin(I).b & mask_n[0]) == mask_n[0]) this->insert(I,I,0.25*x.v);
          if((B.bin(I).b & mask_n[1]) == mask_n[1]) this->insert(I,I,0.25*x.v);
          if((B.bin(I).b & mask_n[2]) == mask_n[2]) this->insert(I,I,-0.25*x.v);
          if((B.bin(I).b & mask_n[3]) == mask_n[3]) this->insert(I,I,-0.25*x.v);
        }
      }

      // first off diagonal terms
      double fac = 0.25;
      if(dir == 'H') fac = 0.5;

      if(dir != 'Z'){
        for(size_t I=0; I<B.dim; ++I){
          int pauli_phase;
          binary_state ssp;
          
          binary_state ss = B.bin(I);// binary form of state 'label'
          auto R = group->Representative(ss, _sec.irrep);

          ssp = ss;
          pauli_phase = ssp.pair_annihilate(binary_state::mask(x.c+n,n), binary_state::mask(x.r,n));
          pauli_phase *= ssp.pair_create(binary_state::mask(x.r+n,n), binary_state::mask(x.c,n));
          if(pauli_phase!=0){
            auto Rp = group->Representative(ssp, _sec.irrep);
            if(pauli_phase==-1) Rp.phase += group->g;
            size_t J = B.index(Rp.b);
            if(J<B.dim) {
              // finding the phase
              X = fac * group->phaseX<HS_field>(Rp.phase) * x.v * sqrt((1.0*R.length)/Rp.length);
              this->insert(J,I,X);
            }
          }
          ssp = ss;
          pauli_phase = ssp.pair_annihilate(binary_state::mask(x.r+n,n), binary_state::mask(x.c,n));
          pauli_phase *= ssp.pair_create(binary_state::mask(x.c+n,n), binary_state::mask(x.r,n));
          if(pauli_phase!=0){
            auto Rp = group->Representative(ssp, _sec.irrep);
            size_t J = B.index(Rp.b);
            if(J<B.dim) {
              X = fac * group->phaseX<HS_field>(Rp.phase) * x.v * (pauli_phase*sqrt((1.0*R.length)/Rp.length));
              this->insert(J,I,X);
            }
          }
        }
      }
    
        // second off diagonal terms
      fac = 0.25;
      if(dir == 'Y') fac = -0.25;

      if(dir == 'X' or dir == 'Y'){
        for(size_t I=0; I<B.dim; ++I){
          int pauli_phase;
          binary_state ssp;
          
          binary_state ss = B.bin(I);// binary form of state 'label'
          auto R = group->Representative(ss, _sec.irrep);
          

          ssp = ss;
          pauli_phase = ssp.pair_annihilate(binary_state::mask(x.c+n,n), binary_state::mask(x.r+n,n));
          pauli_phase *= ssp.pair_create(binary_state::mask(x.r,n), binary_state::mask(x.c,n));
          if(pauli_phase!=0){
            auto Rp = group->Representative(ssp, _sec.irrep);
            if(pauli_phase==-1) Rp.phase += group->g;
            size_t J = B.index(Rp.b);
            if(J<B.dim) {
              // finding the phase
              X = fac * group->phaseX<HS_field>(Rp.phase) * x.v * sqrt((1.0*R.length)/Rp.length);
              this->insert(J,I,X);
            }
          }
          ssp = ss;
          pauli_phase = ssp.pair_annihilate(binary_state::mask(x.r,n), binary_state::mask(x.c,n));
          pauli_phase *= ssp.pair_create(binary_state::mask(x.c+n,n), binary_state::mask(x.r+n,n));
          if(pauli_phase!=0){
            auto Rp = group->Representative(ssp, _sec.irrep);
            size_t J = B.index(Rp.b);
            if(J<B.dim) {
              X = fac * group->phaseX<HS_field>(Rp.phase)  * x.v * (pauli_phase*sqrt((1.0*R.length)/Rp.length));
              this->insert(J,I,X);
            }
          }
        }
      }

    }
    this->sort_elements();
  }
};


#endif
