function dqc-summary() {
        cat $@ | grep " profile:" | GREP_COLOR='01;31' egrep --color=always 'ERROR|$' | GREP_COLOR='01;33' egrep -i --color=always 'WARNING|$' | GREP_COLOR='01;32' egrep -i --color=always 'INFO|$'
}

function dqc-errors() {
        cat $@ | grep -E "ERROR|WARNING" | GREP_COLOR='01;33' egrep --color=always 'WARNING|$' | GREP_COLOR='01;31' egrep -i --color=always 'ERROR|$'
}

