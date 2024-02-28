# loglog

A simple way of taking notes with absolute minimum structure. Everything is a list, even the list items are lists.

## Motivation
I log a lot of things in the following format:

```
- is a dolor sit amet, consectetur adipiscing elit. Vestibulum gravida porta dapibus.
    - delves into the euismod rhoncus elit, quis tempor nulla luctus.
        - offers a ultricies consectetur ipsum sit amet, condimentum aliquet mi.
            - Further magna sed, consequat ac nibh. Donec ut mauris eget.
    - discusses another vehicula velit ac, feugiat ultricies nisi.
        - explores tincidunt lobortis purus, nec efficitur elit vulputate.
        - analyzes the consequat ac, rhoncus nec eros. Nulla facilisi.
            - Examination of vestibulum ullamcorper dolor, vel vehicula dui ullamcorper.
- focuses on: a venenatis magna. Mauris fermentum, magna id mollis.
    - examines various cursus, posuere at semper ut, posuere in ipsum.
        - investigates a tempor justo, id ullamcorper magna finibus.
        - evaluates:
            - discusses lorem ipsum
            - Further gravida lectus, sed efficitur ligula venenatis vitae.
                - offers a ultricies consectetur:
                    - Further magna sed, consequat ac nibh. Donec ut mauris eget.
                    - analyzes the consequat ac, rhoncus nec eros. Nulla facilisi.
            - offers quam. Praesent sit amet velit nec diam.
    - presents: ipsum. Sed vitae ligula eget libero congue.
    - Additional vehicula justo, quis tristique metus aliquam eget.
        - discusses a lorem ipsum, non vehicula nisl lacinia.
    - Comparative consequat quam, et porttitor ipsum vehicula nec.
- offers a pellentesque aliquam:
    - explores a vestibulum condimentum nisi, in condimentum magna gravida.
        - investigates the luctus metus, vitae commodo nulla molestie.
            - In-depth fermentum eros, eget condimentum arcu commodo vitae.
            - evaluates the viverra lorem, sed tempor orci varius.
    - examines another tempor. Sed accumsan tellus eu nisl faucibus.
- addresses an nisi. Donec ultricies mauris eu justo fermentum.
    - discusses a lorem ipsum, non vehicula nisl lacinia.
        - analyzes the aliquet. Curabitur vel sagittis felis.
        - explores eleifend. Sed ac ipsum eget metus.
            - Examination of lorem ipsum, id tempus purus hendrerit.
- provides: a semper, eget consequat odio. Nam tristique nunc ac consequat.
    - delves into the suscipit semper, et sodales libero sollicitudin vitae.
        - offers quam. Praesent sit amet velit nec diam.
        - presents ipsum. Sed vitae ligula eget libero congue.
            - Additional vehicula justo, quis tristique metus aliquam eget.
        - Comparative consequat quam, et porttitor ipsum vehicula nec.
```

This has several benefits:
- Mainly it reduces the overhead of structure for when I'm taking notes. I don't need to think about whether this is a title, heading 1, section, subsection, list, etc. I can freely write down the flow of my thoughts.
- It also is very flexible. By simple indentation I can put a whole section under another item or move things around.
- If I'm using a text editor that folds text, I can easily fold/unfold sections at various levels.
- When a topic gets too big, or if I need a new document around a certain topic, I can just copy that part to a new file and adjust the indentation.
- It is highly portable, i.e. this is a raw text file that I can easily turn it into a markdown, or into other rich formatted texts.
- It is cross platform. Any platform can read/edit a text file.
- I can algorithmically manipulate/analyze it, which is the goal of this repo.

## Functionality
The python code is going to be able to read a text file like above and provide some functionality:

- [x] create a tree data structure that represents the structure of the text.
- [x] handle empty lines, empty items, items with different types:
    - `regular` items start with nothing, or with `-`.
    - `todo` items start with `[]` or `[x]` or `[?]` and have "done" status which is `True`, `False`, or `Null`.
        - I'm not quite sure about the syntaxing here. Maybe I can be a bit more flexible to allow compatibility, but then that adds more structure. I think keeping things simple is better.
- [ ] understand whether an item is a "title" or a "text", or maybe a combination of both. here are some examples:
    ```
        - example:
            - the above item is a title, and below it are a few items regarding it.
            - and this is just a text item, there is not much else you would expect to see
        - another example: but this is a combination, first there is a title of a few words, then a colon, then a longer sentence. There might still be some items below it or not
    ```
- [ ] prints the cleaned up version of the file to the text file.
    - [x] prints only a node and its children
    - [ ] prints the children to a certain depth
- [ ] convert
    - [ ] to markdown
    - [ ] to latex
        - [ ] to pdf
    - [ ] to html
