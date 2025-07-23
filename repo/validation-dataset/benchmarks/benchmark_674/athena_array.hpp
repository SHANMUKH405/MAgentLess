#pragma once
#include <vector>

constexpr int IDN=0;
constexpr int IM1=1;
constexpr int IM2=2;
constexpr int IM3=3;
constexpr int IEN=4;
constexpr int IVX=5;
constexpr int IVY=6;
constexpr int IVZ=7;
constexpr int NHYDRO=8;
constexpr double GAMMA=1.4;

template<typename T>
struct AthenaArray {
    int nvar, nk, nj, ni;
    std::vector<T> data;
    AthenaArray(int nvar,int nk,int nj,int ni)
        : nvar(nvar), nk(nk), nj(nj), ni(ni), data(nvar*nk*nj*ni) {}
    T& operator()(int n,int k,int j,int i) {
        return data[((n*nk + k)*nj + j)*ni + i];
    }
    const T& operator()(int n,int k,int j,int i) const {
        return data[((n*nk + k)*nj + j)*ni + i];
    }
};
