# catmeme retriever

In the long history of cat memes, people who have too much spare time (like me) do need a curated collection of good ones.

### Installation
```bash
pip install catmemes
```
Make sure to set terminal font as [cica](https://github.com/miiton/Cica) to better support CJK alignment in ascii art.


## CLI ascii cats
Adopt four ascii cats:
```
　　　　 ∧___∧　　　   ∧___∧　　　　　　　　　　            ∧  ∧___
　　　　(　´∀` )　　　( ・∀・)　　　　　　　　　　　　　　  /(*ﾟーﾟ)./\
　　　　(　　  )　　  ( 　　 )　　　　　　　　　∧ ∧　 　  /|￣U U￣|\/
　　　  |  |  | 　 　|  |  | 　　　 ～′￣￣(,,ﾟДﾟ)　 　  |　 　  |/
　　　　(___)__）　　 (___)__)　　　　  UU￣U U           ￣￣￣￣

        Mona        Moralar          Giko             Shii
```
The full collection of derivatives is available [here](https://nonexistentfandomsfandom.neocities.org/AAcats/cast).


### Usage
Adopt a cat by name
```bash
ascii-cat list         # list all cat names
ascii-cat [cat_name]   # you guys have too much spare time ~
```

## Iconic cat memes

Search for the most relevant meme from a self-collected dataset

<p align="left">
  <img src="demo_1.gif" alt="bike cat" width="350"/>
  <img src="demo_0.gif" alt="Nyan Cat" width="350"/>
</p>

### Usage
Create conda environment:
```bash
conda create -n catmemes python=3.13
conda activate catmemes
pip install -r requirements.txt
```

Start backend and frontend by running the following two commands in `backend` and `frontend` folder:
```bash
uvicorn app:app --reload --port 8000
npm run dev
```

Find the history of each meme [here](https://knowyourmeme.com/).


## Acknowlegement

Partially inspired by this [Youtube video](https://www.youtube.com/watch?v=PKdUvW8fMj0). In tribute to the iconic feline celebrities who have brought joy to millions.

And I miss my cat *kupo*.

<!-- **TODOs**
- [ ] add google trend index when I have the API access -->
