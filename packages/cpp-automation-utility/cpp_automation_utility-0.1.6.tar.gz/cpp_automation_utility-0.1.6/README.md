# CAU

CAU stands for **C**++ **A**utomation **U**tility and is pronounced  like *cow* :cow2:. The purpose is to provide templates and CLI scripts to instantiate/manage/run C++ projects in a devops environment. CAU covers common functionality across projects like:

* Running a static analyzer (`clang-tidy`)
* Running a memory leak test (`valgrind`)
* Running unit tests
* Restore dependencies (`conan`)
* Building the project (`conan` and `cmake`)
* Providing CI/CD templates for `gitlab`

The scope of CAU is really meant for how we do C++ projects at AldridgeSoftwareDesigns. As such, mileage may vary when applying to projects outside the "standard" configuration for an AldridgeSoftwareDesigns C++ project.
