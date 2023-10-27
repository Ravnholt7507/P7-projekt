    fig = plt.figure(1)
    plt.subplot()
    with open(pltName, 'rb') as file:
        fig = pickle.load(file)
    plt.show()