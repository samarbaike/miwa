import excuse from './not_found.png';

function NotFound() {
    return (
    <div>
        <img src={excuse} alt="Sorry bro" width={300} height={200}/>
    </div>
    )
}

export default NotFound;