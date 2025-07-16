# Todos

- [] Pick up item behavior
- [] Has item in vicinity command with parameters `radius`

```
Idee:
Individuals sense their environment and make decisions based on their goals.

Questions: How to achieve higher order thinking and coordination?

split out Sensoring

alarmed
    - fight
    - flee
calm
    - patrol
    - move around randomly
nervous
    - investigate

sensoring:
    - enemy detected event, target picker
    - usable item detection
    - write to blackboard
    -

```

Hey, which items Am I interested in?
Which items are around me?
Which items of those in my vicinity are interesting?

```log
interests = static, predefined in npcs.yml

blackboard (= runtime state)

each turn:
- Sensing -> what is around me? Given Interests, write into the blackboard where each point of interest is within some range.
- Planning -> Given priority given by Interests and the sensing results (and maybe blackboard as memory/previous knowledge!), decide on a course of action
- Execution -> do actions according to highest priority
```
