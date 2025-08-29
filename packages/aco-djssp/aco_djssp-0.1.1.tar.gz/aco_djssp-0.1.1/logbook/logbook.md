# Logbook

## 27/05/2025
- **Present**: Benjamin Gorrie, Marijan Beg
- **Key points discussed**
    - Initial discussion regarding first steps for the project. It was determined that after some precursory literature review regarding ACO (ant colony optimisation), I would begin to implement an ACO python package and begin to apply it to the [travelling salesman problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem), with the idea being to use this package to solve another problem (such as feature selection) later on.
    - Github repo health was discussed, as well as making sure I familiarise myself with the academic integrity expectations of the IRP.
    - The project plan was also mentioned, and that I should start considering what I might want to include in it.
- **Feedback received**
    - The initial plan was well received, and Marijan suggested meeting a minimum of once every two weeks (ideally once a week) to ensure that I stay on course.
- **Plan before next meeting**:
    - Read existing papers on ACO and start building a bibliography.
    - Try to get a local latex install running (overleaf can be used as a backup if this does not work).
    - At least get some initial ant simulation running, even if it not perfect.

## 04/06/2025
- **Present**: Benjamin Gorrie (joined online), Marijan Beg
- **Key points discussed**
    - Showing Marijan progress done so far, namely the first implementation of the Ant System. Marijan happy with current results, although some basic visualisations need to be implemented. The ants are within 0.5% of the best path of the [Oliver30 nodes](https://stevedower.id.au/research/oliver-30).
    - It was suggested that I slightly change the structure of the repo by moving items in `aco/` one level up. 
    - The main point raised in the meeting was that I should think of an application that uses this Ant System (or some variant of it). This application should be genuinely interesting to me so as not to lose my interest over the course of the project. The initially suggested feature selection idea is probably going to be difficult to implement. Marijan raised the possiblity of using the aco package to solve a scheduling problem or aid the job distribution system that is currently in use in the imperial HPC. This is the main thing I want to have an idea of before next meeting.
- **Feedback received**
    - The current implementation was well received, although it will probably be more clear what is actually going on once some visualisations are produced.
- **Plan before next meeting**
    - Code some basic visualisation functions.
    - Change the directory structure as requested.
    - Think of an interesting and potential novel applications of the Ant System.

## 10/06/2025
- **Present**: Benjamin Gorrie, Marijan Beg
- **Key points discussed**
    - Showed Marijan current basic visualisations. The path one in particular is helpful to determine what the ants end up doing.
    - The main topic discussed was the direction that the project is going to take moving forward, i.e. what should this Ant System be applied to?
    - I suggested a dynamic job-shop scheduling problem (DJSP) that can be solved by the ants. The example I gave was in a hospital, where surgeries overrun/there are emergency arrivals/some machines stop working. In this context, is it possible to reschedule the doctor's existing schedule while causing as minimal a disruption as possible? Is it possible to do this quickly without rescheduling everything from scratch (leveraging the pheromone trails left behind by the ants)? Marijan liked this idea, and stressed that while the context is good for motivating the problem, the package should be as application-agnostic as possible.
    - The project plan deadline was also brought up.
- **Feedback received**
    - DJSP seems to be a good direction to take.
- **Plan before next meeting**
    - Finish the project plan before the deadline.
    - Once this is done, start working on a scheduler using ants. Start with a static scheduler for now, and then try to make it dynamic later.

## 17/06/2025
- **Present**: Benjamin Gorrie (joined online), Marijan Beg
- **Key points discussed**
    - Showed Marijan current basic state of JSSP solved with ACO. Marijan had good suggestions regarding how the current algorithm could be improved.
    - Marijan saw my project plan and was happy with what was written. 
    - ACO elitism was brought up as an improvement to the current Ant System algorithm. Currently, ants are diverging away from the local/global minimum as the suboptimal pheromone trails are drowning out the current best solution.
- **Feedback received**
    - Marijan happy with the direction, and liked the idea of applying the project to a real hospital schedule.
    - Being smart with data allows to simplify code (e.g. can schedule a job for 1.2 time instead of programming a 0.2 time unit gap between operations).
- **Plan before next meeting**
    - Implement Ant Elitism.
    - Make JSSP solving more robust.
    - Start thinking about how to implement a dynamic DJSSP, depending on how good the static variant performs.

## 24/06/2025
- **Present**: Benjamin Gorrie, Marijan Beg
- **Key points discussed**
    - Showed Marijan MMAS JSSP solver. Marijan happy with state of things.
    - I raised my concerns regarding the solution space for JSSP not being smooth unlike in the TSP, meaning ants need to explore more. Marijan does not see this as a huge issue as the focus of the project is (hopefully) the ability for the ants to quickly react to a dynamic change.
    - Monte Carlo swapping was suggested to come up with an initial schedule in case ants end up being too slow.
    - Marijan also bought up starting to work on my final report, maybe like 500 words a week to avoid having to cram it all at the end.
- **Feedback received**
    - Current implementation is close to "good enough", start working on dynamic system.
- **Plan before next meeting**
    - Start working on a DJSSP solver using the MMAS code.
    - Start working on the final project latex files.

## 08/07/2025
- **Present**: Benjamin Gorrie, Marijan Beg
- **Key points discussed**
    - Showed Marijan initial DJSSP solver, simulation runner and visualisation tool (Gantt chart).
    - Discussed metrics other than makespan (like measuring "disruption" for a schedule).
- **Feedback received**
    - Add more types of dynamism: currently only able to add new jobs, but what if machine breaks down, operation overruns etc.
- **Plan before next meeting**
    - Fix time travelling ants.
    - Think about metrics other than makespan.

## 22/07/2025
- **Present**: Benjamin Gorrie, Marijan Beg
- **Key points discussed**
    - Showed Marijan updated DJSSP solver. Large parts of my time spent fixing "time travelling" ants.
    - Discussed metrics other than makespan again. This is the next thing I need to develop.
    - Showed Marijan the priority system the ants currently implement. Marijan seemed happy with this
- **Feedback received**
    - Once the new metric is developed, keep track of how it evolves as new features are added.
- **Plan before next meeting**
    - Develop new metric to measure performance.

## 29/07/2025
- **Present**: Benjamin Gorrie (joined online), Marijan Beg
- **Key points discussed**
    - New "cost" metric which takes into account disruptiveness to an already existing schedule was demonstrated.
    - Reusing previously existing "best" pheromone matrix was also implemented and showed.
    - Discussion regarding best practices for preveneting the large amounts of arguments in main function. Marijan said that I have approached this in a C++ style, and Python usually prefers to not have a main function.
- **Feedback received**
    - Cost metric is good.
    - Work on implementing new dynamism.
- **Plan before next meeting**
    - Refactor existing code to be more pythonic.
    - Add a new type of dynamism.
    - Create a Jupyter Notebook demonstrating how to use the code.
    - Try to get code to run on a real hospital schedule.

## 19/08/2025
- **Present**: Benjamin Gorrie (joined online), Marijan Beg
- **Key points discussed**
    - Discussed writing the final report and reusing the project plan.
    - Discussed publishing package to PyPI.
    - Discussed running the code on a real hospital schedule.
- **Feedback received**
    - Get writing and get scheduling.
- **Plan before next meeting**
    - Finish project draft for Marijan to see.
