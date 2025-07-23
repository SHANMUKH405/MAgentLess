#include <vector>
#include <array>
#include <cmath>
#ifdef _OPENMP
#include <omp.h>
#endif

struct Vec3 {
    double x, y, z;
    Vec3(double xx=0, double yy=0, double zz=0) : x(xx), y(yy), z(zz) {}
    void add(const Vec3& o) { x += o.x; y += o.y; z += o.z; }
    Vec3& operator/=(double v) { x /= v; y /= v; z /= v; return *this; }
};

struct Mesh {
    std::vector<Vec3> nodeCoords;
    std::vector<std::array<int,8>> elements;
    std::vector<std::vector<int>> elementsUsingNode;
};

static std::array<Vec3,8> compute_gradients(const std::array<Vec3,8>& c,
                                            const std::array<double,8>& v)
{
    std::array<Vec3,8> g;
    for(int i=0;i<8;++i){
        Vec3 acc;
        for(int j=0;j<8;++j){
            acc.x += (v[j]-v[i]) * (c[j].x - c[i].x);
            acc.y += (v[j]-v[i]) * (c[j].y - c[i].y);
            acc.z += (v[j]-v[i]) * (c[j].z - c[i].z);
        }
        g[i]=acc;
    }
    return g;
}

void calculateNodalGradients(const Mesh& mesh,
                             const std::vector<double>& src,
                             std::vector<Vec3>& dst)
{
    size_t nodeCount = mesh.nodeCoords.size();
    dst.assign(nodeCount, Vec3());
#pragma omp parallel for schedule(dynamic)
    for(long nodeIdx=0; nodeIdx<(long)nodeCount; ++nodeIdx)
    {
        const auto& elements = mesh.elementsUsingNode[nodeIdx];
        Vec3 result;
        int nValid = 0;
        for(int eIdx : elements)
        {
            const auto& element = mesh.elements[eIdx];
            std::array<Vec3,8> corners;
            std::array<double,8> values;
            for(int c=0;c<8;++c){
                int n = element[c];
                corners[c] = mesh.nodeCoords[n];
                values[c] = src[n];
            }
            auto grads = compute_gradients(corners, values);
            for(int c=0;c<8;++c){
                if(element[c]==nodeIdx)
                    result.add(grads[c]);
            }
            ++nValid;
        }
        if(nValid>0) result /= static_cast<double>(nValid);
        dst[nodeIdx]=result;
    }
}
