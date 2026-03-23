cmake_minimum_required(VERSION 3.16)

project(OCTAnnotate VERSION 1.0 LANGUAGES CXX)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC_SEARCH_PATHS "${CMAKE_CURRENT_SOURCE_DIR}/source")

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Gui Widgets Sql Xml PrintSupport)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Gui Widgets Sql Xml PrintSupport)

set(OCTANNOTATE_SOURCES
    source/main.cpp
    source/octannotate.cpp
    source/patientdata.cpp
    source/newpatientdialog.cpp
    source/qcustomplot.cpp
    source/autoasmanualdialog.cpp
    source/settingsdialog.cpp
    source/calculate.cpp
    source/readwritedata.cpp
    source/computeerrorsettingsdialog.cpp
    source/dbmanager.cpp
    source/batchprocessingdialog.cpp
    source/infodialog.cpp
)

set(OCTANNOTATE_HEADERS
    source/octannotate.h
    source/patientdata.h
    source/newpatientdialog.h
    source/qcustomplot.h
    source/autoasmanualdialog.h
    source/settingsdialog.h
    source/calculate.h
    source/readwritedata.h
    source/computeerrorsettingsdialog.h
    source/dbmanager.h
    source/batchprocessingdialog.h
    source/infodialog.h
)

set(OCTANNOTATE_FORMS
    source/octannotate.ui
    source/newpatientdialog.ui
    source/settingsdialog.ui
    source/computeerrorsettingsdialog.ui
    source/batchprocessingdialog.ui
    source/infodialog.ui
)

set(OCTANNOTATE_RUNTIME_FILES
    source/licence.html
    source/logoPUEPS.png
    source/logoPUT.png
    source/circ_profile_legend.png
)

if(QT_VERSION_MAJOR GREATER_EQUAL 6)
    qt_add_executable(OCTAnnotate
        MANUAL_FINALIZATION
        ${OCTANNOTATE_SOURCES}
        ${OCTANNOTATE_HEADERS}
        ${OCTANNOTATE_FORMS}
    )
else()
    add_executable(OCTAnnotate
        ${OCTANNOTATE_SOURCES}
        ${OCTANNOTATE_HEADERS}
        ${OCTANNOTATE_FORMS}
    )
endif()

set_target_properties(OCTAnnotate PROPERTIES
    WIN32_EXECUTABLE TRUE
)

target_include_directories(OCTAnnotate PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/source"
)

target_link_libraries(OCTAnnotate PRIVATE
    Qt${QT_VERSION_MAJOR}::Core
    Qt${QT_VERSION_MAJOR}::Gui
    Qt${QT_VERSION_MAJOR}::Widgets
    Qt${QT_VERSION_MAJOR}::Sql
    Qt${QT_VERSION_MAJOR}::Xml
    Qt${QT_VERSION_MAJOR}::PrintSupport
)

foreach(runtime_file IN LISTS OCTANNOTATE_RUNTIME_FILES)
    add_custom_command(TARGET OCTAnnotate POST_BUILD
        COMMAND "${CMAKE_COMMAND}" -E copy_if_different
            "${CMAKE_CURRENT_SOURCE_DIR}/${runtime_file}"
            "$<TARGET_FILE_DIR:OCTAnnotate>"
        VERBATIM
    )
endforeach()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/images")
    add_custom_command(TARGET OCTAnnotate POST_BUILD
        COMMAND "${CMAKE_COMMAND}" -E copy_directory
            "${CMAKE_CURRENT_SOURCE_DIR}/images"
            "$<TARGET_FILE_DIR:OCTAnnotate>/images"
        VERBATIM
    )
endif()

add_custom_command(TARGET OCTAnnotate POST_BUILD
    COMMAND "${CMAKE_COMMAND}" -E make_directory
        "$<TARGET_FILE_DIR:OCTAnnotate>/tools"
    COMMAND "${CMAKE_COMMAND}" -E copy_if_different
        "${CMAKE_CURRENT_SOURCE_DIR}/tools/import_e2e.py"
        "$<TARGET_FILE_DIR:OCTAnnotate>/tools/import_e2e.py"
    VERBATIM
)

install(TARGETS OCTAnnotate
    RUNTIME DESTINATION .
    BUNDLE DESTINATION .
)

install(FILES ${OCTANNOTATE_RUNTIME_FILES}
    DESTINATION .
)

install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/tools/import_e2e.py"
    DESTINATION tools
)

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/images")
    install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/images"
        DESTINATION .
    )
endif()

if(QT_VERSION_MAJOR GREATER_EQUAL 6)
    qt_finalize_executable(OCTAnnotate)
endif()
