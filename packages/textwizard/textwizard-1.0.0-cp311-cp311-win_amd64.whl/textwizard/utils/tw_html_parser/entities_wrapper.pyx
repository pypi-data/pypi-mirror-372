# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from libc.stddef cimport size_t

cdef extern from "entities_hash.h":
    cdef struct Entity:
        const char* name
        const char* value

    Entity* lookup_entity(const char* key, size_t len)

cpdef str lookup_entity_value_py(str key):
    """
    Python-accessible wrapper for the C function `lookup_entity`.
    """
    cdef const char* result
    cdef size_t key_len = len(key.encode("utf-8"))
    result = lookup_entity_value(key.encode("utf-8"), key_len)
    if result:
        return result.decode("utf-8")
    return None

# Internal C function (not directly accessible from Python)
cdef inline const char* lookup_entity_value(const char* key, size_t len):
    cdef Entity* result = lookup_entity(key, len)
    if result:
        return result.value
    return NULL
