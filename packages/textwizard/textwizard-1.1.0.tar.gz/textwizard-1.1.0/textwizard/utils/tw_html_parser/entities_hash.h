// SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
// SPDX-License-Identifier: BSD-3-Clause

#ifndef ENTITIES_HASH_H
#define ENTITIES_HASH_H

#include <stddef.h>

struct Entity {
    const char* name;
    const char* value;
};

struct Entity* lookup_entity(const char* key, size_t len);

#endif // ENTITIES_HASH_H
