#include <vector>
#include <array>
#include <chrono>
#include <iostream>
#include <string>
#include <cmath>

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

// Function implemented in the benchmark sources (original.cpp/optimized.cpp)
void calculateNodalGradients(const Mesh&, const std::vector<double>&, std::vector<Vec3>&);

inline int idx(int i,int j,int k,int N) { return i + j*N + k*N*N; }

Mesh createMesh(int N)
{
    Mesh m;
    m.nodeCoords.resize(N*N*N);
    for(int k=0;k<N;++k)
        for(int j=0;j<N;++j)
            for(int i=0;i<N;++i)
                m.nodeCoords[idx(i,j,k,N)] = Vec3(i,j,k);

    m.elements.reserve((N-1)*(N-1)*(N-1));
    m.elementsUsingNode.assign(N*N*N, {});
    for(int k=0;k<N-1;++k)
        for(int j=0;j<N-1;++j)
            for(int i=0;i<N-1;++i) {
                std::array<int,8> e = {
                    idx(i,j,k,N),     idx(i+1,j,k,N),
                    idx(i,j+1,k,N),   idx(i+1,j+1,k,N),
                    idx(i,j,k+1,N),   idx(i+1,j,k+1,N),
                    idx(i,j+1,k+1,N), idx(i+1,j+1,k+1,N)
                };
                int eid = m.elements.size();
                m.elements.push_back(e);
                for(int v : e) m.elementsUsingNode[v].push_back(eid);
            }
    return m;
}

int main(int argc, char* argv[])
{
    std::string mode = "perf";
    int grid = 40;
    int repeat = 400;

    for(int i=1;i<argc;++i){
        std::string arg = argv[i];
        if(arg=="--mode=correct") mode = "correct";
        else if(arg=="--mode=perf") mode = "perf";
        else if(arg.rfind("--grid=",0)==0) grid = std::stoi(arg.substr(7));
        else if(arg.rfind("--repeat=",0)==0) repeat = std::stoi(arg.substr(9));
    }

    Mesh mesh = createMesh(grid);
    std::vector<double> values(mesh.nodeCoords.size());
    for(size_t i=0;i<values.size();++i) values[i] = std::sin(double(i));
    std::vector<Vec3> out;

    if(mode=="correct") {
        calculateNodalGradients(mesh, values, out);
        double sum = 0.0;
        for(const auto& v : out) sum += v.x + v.y + v.z;
        std::cout << sum << '\n';
    } else {
        using clock = std::chrono::high_resolution_clock;
        auto t1 = clock::now();
        for(int r=0;r<repeat;++r) calculateNodalGradients(mesh, values, out);
        auto t2 = clock::now();

        std::cout << "Time: " << std::chrono::duration_cast<std::chrono::milliseconds>(t2-t1).count() << " ms\n";
    }
}

