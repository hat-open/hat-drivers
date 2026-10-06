BEGIN { FS = ":[[:space:]]*" }

/^>>> L4/ { p = 1 }
/^$/      { p = 0 }
!p        { next }

/^[[:space:]]*function_group:/ { fg = $2 + 0 }
/^[[:space:]]*type:/           { type = $2 + 0 }
/^[[:space:]]*data:/           { print fg ", " type ": " $2 }
