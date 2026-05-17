import math as m
from scipy .stats import norm
import matplotlib.pyplot as plt

def BlackScholesModel(S, K, T, sigma, r, PutCall):
    d1 = (m.log(S/K) + (r + (sigma **2)/2.0)*T) / (sigma *m.sqrt (T))
    d2 = (m.log(S/K) + (r - (sigma **2)/2.0)*T) / (sigma *m.sqrt (T))

    if PutCall == 'C':
        optionPrice = S*norm.cdf(d1)-K*m.exp(-r*T)*norm .cdf(d2)
    elif PutCall == 'P':
        optionPrice = K*m.exp(-r*T) - S + S*norm .cdf(d1)-K*m.exp(-r*T)*norm .cdf(d2)

    return optionPrice


def BinomialModel(s, K, T, sigma, r, PutCall, EuroAmer, n):
    dt = T/n
    u = m.exp(sigma *m.sqrt (dt))
    d = 1.0/u
    p = (m.exp(r*dt) - d) / (u - d)
    rows = n+1
    cols = n+1

    S = [[0 for i in range (cols )] for j in range (rows)]
    for j in range (cols):
        for i in range (rows):
            S[i][j] = s*pow(u, j-i) * pow(d, i)

    V = [[0 for i in range (cols )] for j in range (rows)]
    for i in range (rows ):
        if PutCall == 'C':
            V[i][n] = max(S[i][n]-K, 0.0)
        elif PutCall == 'P':
            V[i][n] = max(K-S[i][n], 0.0)

    for j in range (n-1, -1, -1):
        for i in range (j+1):
            Vij = m.exp(-r*dt)*(p*V[i][j+1] + (1-p)*V[i+1][j+1])
            
            if EuroAmer == 'E':
                V[i][j] = Vij
            elif EuroAmer == 'A':
                if (PutCall == 'C'):
                    V[i][j] = max(S[i][j]-K, Vij)
                elif PutCall == 'P':
                    V[i][j] = max(K-S[i][j], Vij)

    return V[0][0]


def TrinomialModel(s, K, T, sigma, r, PutCall, EuroAmer, n):
    dt = T/n
    u = m.exp(sigma *m.sqrt (2.0*dt))
    d = 1.0/u
    pu = pow ( (m.exp(0.5*r*dt) - m.sqrt (d)) / (m.sqrt (u) - m.sqrt (d)) ,2)
    pd = pow ( (m.sqrt (u) - m.exp(0.5*r*dt)) / (m.sqrt (u) - m.sqrt (d)) ,2)
    pm = 1-pu-pd
    rows = 2*n+1
    cols = n+1

    S = [[0 for i in range (cols )] for j in range (rows)]
    for j in range (cols):
        for i in range (rows ):
            S[i][j] = s*pow (u, j-i)

    V = [[0 for i in range (cols )] for j in range (rows)]
    for i in range (rows):
        if PutCall == 'C':
            V[i][n] = max(S[i][n]-K, 0.0)
        elif PutCall == 'P':
            V[i][n] = max(K-S[i][n], 0)

    for j in range (n-1, -1, -1):
        for i in range(2*j+1):
            Vij = m.exp(-r*dt)*(pu*V[i][j+1] + pm*V[i+1][j+1] + pd*V[i+2][j+1])

            if EuroAmer == 'E':
                V[i][j] = Vij
            elif EuroAmer == 'A':
                if (PutCall == 'C'):
                    V[i][j] = max(S[i][j]-K, Vij)
                elif PutCall == 'P':
                    V[i][j] = max(K-S[i][j], Vij)

    return V[0][0]


def PutCallParity (S, K, T, r, PutCall, X):
    if PutCall == 'C':
        res = X + K*m.exp(-r*T) - S
    elif PutCall == 'P':
        res = X + S - K*m.exp(-r*T)

    return 


def convergence_plot(s, K, T, sigma, r, PutCall, EuroAmer, step, n_max):
    n_values = range(step, n_max + 1, step)
    binomial_results = []
    trinomial_results = []
    binomial_errors= []
    trinomial_errors = []
    bs_value = BlackScholesModel(s, K, T, sigma, r, PutCall)

    for n in n_values:
        bin_price = BinomialModel(s, K, T, sigma, r, PutCall, EuroAmer, n)
        tri_price = TrinomialModel(s, K, T, sigma, r, PutCall, EuroAmer, n)

        binomial_results.append(bin_price)
        trinomial_results.append(tri_price)

    binomial_errors = abs(binomial_results - bs_value)
    trinomial_errors = abs(trinomial_results - bs_value)
    
    #plt.plot(n_values, binomial_results, label="Binomial Model")
    #plt.plot(n_values, trinomial_results, label="Trinomial Model")

    plt.plot(n_values, binomial_errors, label="Binomial Model")
    plt.plot(n_values, trinomial_errors, label="Trinomial Model")

    plt.xlabel("n (number of steps)")
    plt.ylabel("Option Price")
    plt.title("Convergence of Binomial vs Trinomial Models")
    plt.legend()
    plt.show()

    return binomial_results, trinomial_results


if __name__ == "__main__":
    convergence_plot(100.0, 100.0, 3.0, 0.2, 0.05, 'C', 'E', 100, 3000)