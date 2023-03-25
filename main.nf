process test {

    container 'r-base:4.0.0'
    
    script:
        """
        R -e 2 + 2
        """
}

workflow {
    test()
}
