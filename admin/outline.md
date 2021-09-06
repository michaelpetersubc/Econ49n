# Econ 4?? Topics in Computational and Theoretical Game Theory
## Instructor Michael Peters
Vancouver School of Economics

https://montoya.econ.ubc.ca

September - December 2021

## Course Objectives

The course consists of a series of topics that illustrate the complementary relationship between computation and game theory.  

1. Students will learn how to use theoretical methods like fixed points along with computational solvers in julia and python to make numerical inferences about preferences from data from experiments and online auctions. The intent is to show them what a rich tool game theory is when dealing with complex environments. 

2. Students will learn how to apply basic models of directed search to networks in order to derive value based rankings of nodes in a network.  This provides a theoretical foundation for methods like the google page rank.  Illustrations are provided in the academic job market to evaluate graduate schools.

3. Students will learn the principles of algorithms and how they are used to guide matching and generate prices.  Applications include school matching.

4. Finally students will learn how to use 'worst case' or prior free mechanism design to evaluate what parts of an economic environment are 'important' when designing allocation and pricing rules.

## Course Materials and Requirements.

There is no textbook for the course, all readings,notebooks and many datasets will be available online.

Computational tools include jupyter notebooks, python and julia.

Meetings will occur bi-weekly on Tuesday and Thursday.  There will be presentations by multiple speakers.

Grades will be based on three projects, one theoretical and two computational.  These will involve three presentations.  These will be evaluated by more than one faculty member.

Projects are due February 5, March 5 and April 5.  Each is worth one third of the final grade.


## Readings
The following is a preliminary list of readings and associated data sets. 

* Week 1. Review of Bayesian Equilibrium and its interpretation as a fixed point  - https://montoya.econ.ubc.ca/Econ600/bayesian.pdf
* Week 2. Theory of Directed Search notebook - https://montoya.econ.ubc.ca/Econ600/directed_search.pdf 
* Week 3. How to use computer algebra to find fixed points. 
    https://github.com/michaelpetersubc/notebooks/blob/master/Econ306/directed_search/directed_search_2.ipynb
* Week 4. Experiments - Identifying Higher Order Rationality by Terri Kneeland, Econonmetrica, Volume 83, issue 5 September 2015 
  * Data from the experiment - https://github.com/michaelpetersubc/notebooks/tree/master/Econ515/ring_game
  * Maximum Likelihood estimation https://montoya.econ.ubc.ca/Econ306/terri_experiment.pdf
* Week 5. An experiment to estimate loss aversion using the Ultimatum Game - https://montoya.econ.ubc.ca/Econ600/mike_reference_offer.pdf
    * Data from the experiment. - https://github.com/michaelpetersubc/notebooks/tree/master/Econ515/ultimatum_game
* Week 6. The theory of Auctions - https://montoya.econ.ubc.ca/Econ600/auctions.pdf
  * Data from eBay - computer chips - https://github.com/michaelpetersubc/notebooks/tree/master/processors
  * Data from eBay - cameras - https://github.com/michaelpetersubc/notebooks/tree/master/eBay
* Week 7. Matching and algorithms
  * Deferred Acceptance - http://montoya.econ.ubc.ca/Econ600/matching.pdf
  * Text version and a case study](http://montoya.econ.ubc.ca/Econ306/deferred_acceptance.pdf
* Week 8. The Hungarian Algorithm - https://montoya.econ.ubc.ca/Econ514/hungarian.pdf
* Week 9. Vizing Algorithm https://montoya.econ.ubc.ca/Econ600/vizing.pdf - a special case of graph coloring used in spectrum auctions.
* Week 10. The Academic Job Market - https://sage.microeconomics.ca - courtesy of Amedeus D'Souza
  * Identifying Types using a Stochastic Greedy Algorithm  - https://github.com/michaelpetersubc/smb_project
* Week 11. Bayes Nash Equilibrium - Approximation
  * from Jason Hartline's textbook - http://jasonhartline.com/MDnA/MDnA-chX.pdf
* Week 12. Ranking Methods
  * Axioms Characterizing the Google Page Rank - https://www.cse.huji.ac.il/~noam/econcs/p1-altman.pdf Altman and Tenneholtz
* Week 13. Page rank using academic placement data - https://montoya.econ.ubc.ca/svn-econ/Econ515/notebooks/ejm/

## A recommended video  - 
Tim Roughgarden Reverse Spectrum Auctions 
- https://www.youtube.com/watch?v=jf_2_XHrpmE&list=PLEGCF-WLh2RK6lq3iSsiU84rWVee3A-hz&index=38
