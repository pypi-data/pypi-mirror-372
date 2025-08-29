#include <string>

/**
 * @brief Returns a string with contents, "Hello, World"
 *
 * @return std::string "Hello, World"
 */
[[nodiscard]] auto HelloWorld() -> std::string;

{% if header_only -%}
auto HelloWorld() -> std::string
{
    return std::string{"Hello, World!"};
}
{%- endif %}

