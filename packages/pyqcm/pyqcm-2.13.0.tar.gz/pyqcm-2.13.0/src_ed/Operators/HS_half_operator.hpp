#ifndef HS_half_operator_h
#define HS_half_operator_h

/**
Class HS_half_operator represents a tensor factor in a factorized one-body operator
 */

//! Represents a factor (up or down) of a factorizable one-body operator in a sector of the Hilbert space for up or down electrons
template<typename op_field>
struct HS_half_operator
{
  vector<pair<op_field, vector<pair<uint32_t, uint32_t>>>> v;
  vector<diagonal_matrix_element> diag_elem;
  uint32_t dim;


  HS_half_operator(const vector<matrix_element<op_field>> &elements, shared_ptr<ED_halfbasis> B, bool spin_down){
    dim = B->dim;
    check_signals();
    size_t n = B->L;
    int offset = spin_down ? n : 0;
    op_field X;
    for(size_t I=0; I<dim; ++I){ // loop over basis states
      binary_state ss = binary_state(B->bin[I]);// binary form of 'in' state
      for(auto &x : elements){ // loop over matrix elements of the 1-body operator
        if((x.r >= n and !spin_down) or (x.r < n and spin_down)) continue; // we are only looking at a given spin
        if(x.r != x.c){ // if nondiagonal element
          binary_state ssp(ss); // binary state obtained by applying the matrix element to the state 'ss'
          int pauli_phase = ssp.one_body(binary_state::mask(x.c-offset,n), binary_state::mask(x.r-offset,n)); // computes ssp from ss, with phase
          if(pauli_phase==0) continue; // the hopping is impossible because of the Pauli principle
          size_t J = B->index(ssp.right()); // finds the index of the 'out' state
          if(J==B->dim) continue; // not a valid state in this representation
          X = (1.0*pauli_phase) * x.v;
          this->insert(I,J,X); // inserts in the sparse matrix
                              // no need to add the Hermitean conjugate here, this is done in t
        }
        else if(ss.b&binary_state::mask(x.r-offset,n)) this->insert(I, I, real(x.v)); // diagonal case
      }
    }
    this->sort_elements();
  }

  
  void insert(uint32_t I, uint32_t J, op_field z){
    if(abs(z) < SMALL_VALUE) return;
    else if(J>I) return; // stores only the lower diagonal + diagonal
    else if(J==I) diag_elem.push_back(diagonal_matrix_element(I, real(z)));
    else{
      size_t i;
      for(i=0; i<v.size(); i++){
        if(z == v[i].first){
          v[i].second.push_back({I,J});
          break;
        }
      }
      if(i==v.size()){
        v.push_back({z, vector<pair<uint32_t, uint32_t>>()});
        v.back().second.push_back({I,J});
      }
    }
  }


  void sort_elements(){
    for(auto& x : v) std::sort(x.second.begin(), x.second.end());
    std::sort(diag_elem.begin(), diag_elem.end());
  }

};


#endif
