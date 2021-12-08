#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <vector>
#include <string>
#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>

using namespace std;

bool inline find_data_box(const double *data, const int size_d1, const int size_d2, double coord_d1, double coord_d2, double out[16])
{
    int c_d1 = static_cast<int>(round(coord_d1));
    int c_d2 = static_cast<int>(round(coord_d2));
    int start_d1, end_d1, start_d2, end_d2;
    int real_d1, d1, read_d2, d2, i, j(0);

    start_d2 = c_d2 - 2;
    end_d2 = c_d2 + 2;

    start_d1 = c_d1 - 2;
    end_d1 = c_d1 + 2;

    if (end_d1 < -2 || end_d1 > size_d1 + 4)
    {
        PyErr_SetString(PyExc_ValueError, "invalid size d1 during extract data box");
        return false;
    }

    if (end_d2 < -2 || end_d2 > size_d2 + 4)
    {
        PyErr_SetString(PyExc_ValueError, "invalid size d2 during extract data box");
        return false;
    }

    for (d1 = start_d1; d1 < end_d1; d1++)
    {
        real_d1 = d1;
        if (real_d1 < 0)
        {
            real_d1 = 0;
        }
        else if (real_d1 >= size_d1)
        {
            real_d1 = size_d1 - 1;
        }

        for (d2 = start_d2; d2 < end_d2; d2++)
        {
            read_d2 = d2;
            if (read_d2 < 0)
            {
                read_d2 = 0;
            }
            else if (read_d2 >= size_d2)
            {
                read_d2 = size_d2 - 1;
            }

            i = read_d2 + real_d1 * size_d2;

            out[j] = data[i];
            j++;
        }
    }

    return true;
}

void inline calculate_weight(const int d, const double &scale, const double &a, double coeffs[4])
{
    double f = (d + 0.5) * scale - 0.5;
    f -= floor(f);

    coeffs[0] = ((a * (f + 1) - 5 * a) * (f + 1) + 8 * a) * (f + 1) - 4 * a;
    coeffs[1] = ((a + 2) * f - (a + 3)) * f * f + 1;
    coeffs[2] = ((a + 2) * (1 - f) - (a + 3)) * (1 - f) * (1 - f) + 1;
    coeffs[3] = 1.f - coeffs[0] - coeffs[1] - coeffs[2];
}

double inline bicubic(const double box[16], const double coeffs_d1[4], const double coeffs_d2[4])
{
    double temp, res(0);
    for (int i = 0; i < 4; i++)
    {
        temp = 0;
        for (int j = 0; j < 4; j++)
        {
            temp += coeffs_d2[j] * box[i * 4 + j];
        }
        res += coeffs_d1[i] * temp;
    }

    return res;
}

PyArrayObject *interpolate(PyArrayObject *in, const int size_d1, const int size_d2, const double &a)
{
    PyArrayObject *out;
    npy_intp *shape = PyArray_SHAPE(in);
    npy_intp dim[2] = {size_d1, size_d2};

    const double *data = static_cast<const double *>(PyArray_DATA(in));
    out = (PyArrayObject *)PyArray_SimpleNew(2, dim, NPY_DOUBLE);
    double *out_data = static_cast<double *>(PyArray_DATA(out));
    const unsigned int size = PyArray_SIZE(out);
    // scale = 1 / upsize
    double scale_d1 = static_cast<double>(shape[0]) / static_cast<double>(size_d1);
    double scale_d2 = static_cast<double>(shape[1]) / static_cast<double>(size_d2);

    int d1, d2;
    double coord_d2, coord_d1;
    double coeffs_d1[4], coeffs_d2[4];
    double box[16];
    for (unsigned int i = 0; i < size; i++)
    {
        // dy
        d1 = i / size_d2;
        // dx
        d2 = i % size_d2;
        // step = scale_d, center of pixel = step / 2 + index * step
        coord_d1 = scale_d1 * (d1 + .5);
        coord_d2 = scale_d2 * (d2 + .5);

        // retrieve box
        if (!find_data_box(data, shape[0], shape[1], coord_d1, coord_d2, box))
        {
            return NULL;
        }

        calculate_weight(d1, scale_d1, a, coeffs_d1);
        calculate_weight(d2, scale_d2, a, coeffs_d2);

        out_data[i] = bicubic(box, coeffs_d1, coeffs_d2);
    }

    return out;
}

static PyObject *_interpolate(PyObject *self, PyObject *args)
{
    PyArrayObject *in = NULL, *out;
    int outsize_d1;
    int outsize_d2;
    double a;

    if (!PyArg_ParseTuple(args, "O!iid", &PyArray_Type, &in, &outsize_d1, &outsize_d2, &a))
    {
        PyErr_SetString(PyExc_ValueError, "invalid argument");
        return NULL;
    }

    if (PyArray_NDIM(in) != 2)
    {
        PyErr_SetString(PyExc_ValueError, "input data must be a 2d array");
        return NULL;
    }

    // printf("%s:%d interpolate\n", __FILE__, __LINE__);
    out = interpolate(in, outsize_d1, outsize_d2, a);
    if (out)
    {
        return PyArray_Return(out);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError, "interpolate fail!");
        return NULL;
    }
}

PyMODINIT_FUNC PyInit__bicubic()
{
    import_array();

    static PyMethodDef Bicubic[] = {
        // { name, method, flags, doc }
        {"interpolate", (PyCFunction)_interpolate, METH_VARARGS, "Fill missing data with bicubic interpolation"},
        {NULL, NULL, 0, NULL}};

    static struct PyModuleDef module = {
        // { base, name, doc, size, module’s method table }
        PyModuleDef_HEAD_INIT,
        "_bicubic",
        "Bicubic interpolation",
        -1, // global state
        Bicubic};

    return PyModule_Create(&module);
}
