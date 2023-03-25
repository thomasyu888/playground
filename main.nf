process test {

    container 'r-base:4.0.0'

    input:
        val cohort
    
    script:
        """
        R -e 2 + 2
        """
}

workflow {
    foo = "bar"
    test(foo)
}
