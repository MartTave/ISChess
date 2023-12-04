function funcBidouille1(x)
    return 10 / (x + 0.1)
end

function funcBidouille2(tab)
    k = 0
    tabVals = zeros(0)
    for i in tab
        result = funcBidouille1(i)
        k += result
        append!(tabVals, result)
    end

    out = 0
    for i in range(1,length(tab),step=1)
        out += tabVals[i] * tab[i] / k
    end
    return out
end

begin
    node1 = [10,13,0]
    node2 = [5,5,7]
    node3 = [2,19,37]
    println(funcBidouille2(node1))
    println(funcBidouille2(node2))
    println(funcBidouille2(node3))
end