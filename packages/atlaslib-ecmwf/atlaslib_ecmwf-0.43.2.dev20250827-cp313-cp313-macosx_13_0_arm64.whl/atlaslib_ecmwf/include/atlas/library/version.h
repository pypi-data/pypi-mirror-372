/*
 * (C) Copyright 2013 ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation
 * nor does it submit to any jurisdiction.
 */

#pragma once

namespace atlas {
namespace library {

constexpr const char* version() {
    return "0.43.2.dev20250827";
}

constexpr const char* semantic_version() {
    return "0.43.2";
}

constexpr long semantic_version_major() {
    return 0;
}

constexpr long semantic_version_minor() {
    return 43;
}

constexpr long semantic_version_patch() {
    return 2;
}

}
}
