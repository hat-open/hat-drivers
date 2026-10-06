BEGIN     { p = 0 }
/^>>> L4/ { p = 1 }
/^$/      { p = 0 }
!p        { next }

/^[[:space:]]*function_group:/ {
    split($0, x, ":")
    fg = x[2] + 0
}

/^[[:space:]]*type:/ {
    split($0, x, ":")
    type = x[2] + 0
}

/^[[:space:]]*data:/ {
    sub("[[:space:]]*data:[[:space:]]*", "")
    print fg ", " type ": " $0
}
