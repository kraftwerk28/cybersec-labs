<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  import { sha3_256 } from 'js-sha3';

  function hashpwd(password) {
    return sha3_256(password);
  }

  let mode = null;
  let authorized = false;
  let register = { email: '', password: '' };
  let login = { email: 'kefirchik3@gmail.com', password: '' };
  let header = ['user_id', 'email', 'pwd_hash', 'phone_number'];
  let usersResponse = Promise.resolve([]);

  onMount(() => {
    refreshUsers();
  });

  function onSubmitLogin() {
    const payload = {
      email: login.email,
      password: hashpwd(login.password),
    };
    axios
      .post('/login', payload)
      .then(() => {
        authorized = true;
        alert('Login successfull');
      })
      .catch(alert)
  }

  function onSubmitRegister() {
    const payload = {
      email: register.email,
      password: hashpwd(register.password),
    };
    axios
      .post('/register', payload)
      .then(() => alert('Registered successfully'))
  }

  function refreshUsers() {
    usersResponse = axios.get('/users').then(r => r.data);
  }

</script>

<style>
  table {
    border-collapse: collapse;
  }
  td {
    border: 1px solid;
    padding: 0.5em;
  }
</style>
<main>
  {#if mode === null}
    <button on:click={() => mode = 'login'}>Log in</button>
    <button on:click={() => mode = 'register'}>Register</button>
  {:else if mode === 'register'}
    <button on:click={() => mode = 'login'}>Log in</button>
    <form on:submit|preventDefault={onSubmitRegister}>
      <fieldset>
        <legend>Register</legend>
        <input placeholder="email" type="email" bind:value={register.email} />
        <input
          placeholder="password"
          type="password"
          bind:value={register.password}
        />
        <button type="submit">Register</button>
      </fieldset>
    </form>
  {:else if mode === 'login'}
    <button on:click={() => mode = 'register'}>Register</button>
    {#if !authorized}
      <form on:submit|preventDefault={onSubmitLogin}>
        <fieldset>
          <legend>Login</legend>
          <input placeholder="email" type="email" bind:value={login.email} />
          <input
            placeholder="password"
            type="password"
            bind:value={login.password}
          />
          <button type="submit">Login</button>
        </fieldset>
      </form>
    {/if}
  {/if}

  <div>
    <button on:click={refreshUsers}>Refresh users</button>
  </div>

  {#await usersResponse}
    <code>Loading...</code>
  {:then users}

    <table>
      <tr>
        {#each header as h}
          <td>{h}</td>
        {/each}
      </tr>

      {#each users as user}
        <tr>
          {#each header as key}
            <td>{user[key]}</td>
          {/each}
        </tr>
      {/each}
    </table>

  {/await}

</main>

